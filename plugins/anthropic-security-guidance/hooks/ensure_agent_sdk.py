#!/usr/bin/env python3
"""SessionStart bootstrap: ensure claude_agent_sdk is importable for the
agentic commit reviewer.

If claude_agent_sdk already imports in the current python3, this is a no-op.
Otherwise it creates a venv at ~/.claude/security/agent-sdk-venv and installs
the SDK there. security_reminder_hook.py prepends that venv's site-packages to
sys.path before attempting the SDK import, so the venv is used as a
fallback only when the system install is missing.

The venv lives under ~/.claude/security/ (same dir the plugin already uses
for per-session state) so it persists across plugin updates — rebuilding
on every update is 30-60s of wasted work for a package that changes far
less often than the plugin does.
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import time
from pathlib import Path

# Shared state-dir resolver: SECURITY_WARNINGS_STATE_DIR → CLAUDE_CONFIG_DIR/security
# → ~/.claude/security. See _base.state_dir for resolution precedence. Re-aliased
# here to match the existing local name (state_dir was already a local var in
# main() and _maybe_emit_user_notice).
from _base import state_dir as _resolve_state_dir

# Outcome codes for the sdk_bootstrap metric. Values are stable for telemetry.
NOOP_SYSTEM = 0      # claude_agent_sdk already importable in system python
NOOP_VENV = 1        # venv already built and SDK imports from it
BUILT = 2            # venv created + SDK pip-installed this run
BUILD_FAILED = 3     # venv create or pip install raised/timed out
# Outcome 4 was previously SKIP_WIN32; retired now that the consumer glob in
# llm.py also matches Windows venv layout (Lib/site-packages). Don't reuse the
# value — telemetry rows from older plugin builds still emit 4.
SKIP_SENTINEL = 5    # another SessionStart is currently building
HOOK_PY_INCOMPATIBLE = 6  # hook interpreter is <3.10 — SDK syntax can't load
                          # here no matter how the venv was built. See #2071.


def _sdk_on_syspath() -> bool:
    # find_spec is ~10ms; actually importing the SDK pulls in
    # transitive deps and costs ~800ms — too heavy for a
    # per-SessionStart no-op check that most sessions hit.
    try:
        return importlib.util.find_spec("claude_agent_sdk") is not None
    except Exception:
        return False


def _plugin_version_int() -> int:
    # Same encoding as security_reminder_hook._read_plugin_version_int so
    # metrics rows from both hooks join on pv.
    try:
        p = Path(__file__).parent.parent / ".claude-plugin" / "plugin.json"
        v = json.loads(p.read_text())["version"]
        major, minor, patch = (int(x) for x in v.split(".")[:3])
        return major * 10000 + minor * 100 + patch
    except Exception:
        return 0


def main() -> tuple[int, str, str]:
    """Run the bootstrap. Returns (outcome, err_phase, err_kind).

    err_phase / err_kind are non-empty only on BUILD_FAILED — they let
    telemetry split bootstrap failures by root cause.
    """
    # Honesty check (fixes the misleading NOOP_VENV in #2071): the SDK
    # requires Python >=3.10 and uses 3.10+ syntax (match statements,
    # PEP 604 unions). On a 3.9 hook interpreter we CANNOT import it no
    # matter how the venv was built — llm.py runs in this same interpreter
    # and the syntax-level import will SyntaxError. macOS ships 3.9.6 as
    # the default `python3` and `/usr/bin` precedes Homebrew in PATH, so
    # this case is the default state for a large share of macOS users.
    #
    # sg-python.sh now prefers python3.10+ binaries so most users won't
    # reach this branch; the fallback to 3.9 is preserved for the
    # pattern-warning hooks that don't need the SDK. Reporting
    # HOOK_PY_INCOMPATIBLE here:
    #   (a) avoids 30-60s of wasted pip install,
    #   (b) avoids the lie where the venv_py probe says NOOP_VENV but the
    #       consumer import fails, and
    #   (c) gives telemetry a clean bucket to size the affected fleet.
    if sys.version_info < (3, 10):
        return (
            HOOK_PY_INCOMPATIBLE,
            "hook_py",
            f"py_{sys.version_info[0]}.{sys.version_info[1]}",
        )

    if _sdk_on_syspath():
        return NOOP_SYSTEM, "", ""

    state_dir = Path(_resolve_state_dir())
    venv = state_dir / "agent-sdk-venv"
    # Windows venvs put the interpreter at Scripts\python.exe; POSIX uses bin/python.
    if sys.platform == "win32":
        venv_py = venv / "Scripts" / "python.exe"
    else:
        venv_py = venv / "bin" / "python"

    # Another SessionStart (concurrent CC instance, same plugin) may already
    # be building. The sentinel lives NEXT TO the venv, not inside it —
    # `python -m venv --clear` wipes the target dir's contents, so an
    # in-venv sentinel would be deleted the instant we create the venv.
    # Stale sentinels (>5min) from a SIGKILL'd build are ignored.
    sentinel = state_dir / "agent-sdk-venv.building"
    if sentinel.exists():
        try:
            if time.time() - sentinel.stat().st_mtime < 300:
                return SKIP_SENTINEL, "", ""
            sentinel.unlink(missing_ok=True)
        except OSError:
            return SKIP_SENTINEL, "", ""

    # If a venv already exists and its python can import the SDK, done.
    if venv_py.exists():
        try:
            r = subprocess.run(
                [str(venv_py), "-c", "import claude_agent_sdk"],
                capture_output=True, timeout=10,
            )
            if r.returncode == 0:
                return NOOP_VENV, "", ""
        except Exception:
            pass  # broken venv; rebuild below

    err_phase = ""
    err_kind = ""
    we_own_sentinel = False
    try:
        state_dir.mkdir(parents=True, exist_ok=True)
        # O_EXCL makes the sentinel an atomic lock — if two SessionStarts
        # race past the exists() check above, only one creates it.
        try:
            os.close(os.open(sentinel, os.O_CREAT | os.O_EXCL | os.O_WRONLY))
        except FileExistsError:
            return SKIP_SENTINEL, "", ""
        we_own_sentinel = True
        err_phase = "venv"
        subprocess.run(
            [sys.executable, "-m", "venv", "--clear", str(venv)],
            capture_output=True, timeout=60, check=True,
        )
        # Some machines route pip through a private registry; we
        # don't pass --index-url here so we inherit that default. Outside
        # the user's machine, pip's own default registry applies — that's the same
        # exposure the user would have running `pip install` themselves, so
        # we're not widening the supply-chain surface.
        #
        # --prefer-binary: on ARM64 Windows, pip's default resolver picks a
        # `cryptography` version with no published binary wheel and tries to
        # build from source, which needs Rust/Cargo (almost never present
        # on user machines). The build fails and the whole bootstrap returns
        # BUILD_FAILED. A binary wheel exists on PyPI for an adjacent
        # version (`cryptography-46.0.3-cp311-abi3-win_arm64.whl`);
        # --prefer-binary tells pip to pick it. Cross-platform safe: no-op
        # on platforms where the latest version already has a wheel.
        err_phase = "pip"
        subprocess.run(
            [str(venv_py), "-m", "pip", "install", "--quiet",
             "--disable-pip-version-check", "--prefer-binary",
             "claude-agent-sdk"],
            capture_output=True, timeout=120, check=True,
        )
        return BUILT, "", ""
    except subprocess.CalledProcessError as e:
        # Capture a stderr fingerprint so telemetry can split BUILD_FAILED by
        # root cause (no-network, package-not-found, dns-fail, etc.).
        # Categorize first, then keep a short raw tail for the long tail of
        # unexpected modes.
        stderr_b = e.stderr or b""
        if isinstance(stderr_b, bytes):
            stderr_str = stderr_b.decode("utf-8", errors="replace")
        else:
            stderr_str = str(stderr_b)
        s = stderr_str.lower()
        if "no matching distribution" in s or "could not find a version" in s:
            err_kind = "pip_no_match"
        elif "name or service not known" in s or "name resolution" in s \
                or "nodename nor servname" in s or "temporary failure in name" in s:
            err_kind = "dns_fail"
        elif "connection refused" in s or "connection reset" in s:
            err_kind = "conn_refused"
        elif "ssl" in s and ("verify" in s or "certificate" in s):
            err_kind = "ssl_verify"
        elif "permission denied" in s or "read-only file system" in s:
            err_kind = "perm_denied"
        elif "no module named pip" in s or "no module named ensurepip" in s:
            err_kind = "no_pip"
        elif "no space left" in s or "disk quota" in s:
            err_kind = "disk_full"
        elif "proxy" in s and ("authent" in s or "tunnel" in s or "407" in s):
            err_kind = "proxy_auth"
        elif "timeout" in s or "timed out" in s:
            err_kind = "stderr_timeout"
        else:
            # First 60 chars of the last non-empty stderr line — bounded to
            # stay inside CC's metric value-length budget. Real failure modes
            # we haven't categorized show up here as a low-cardinality bucket.
            tail = next(
                (ln.strip() for ln in reversed(stderr_str.splitlines()) if ln.strip()),
                "",
            )[:60]
            err_kind = f"other:{tail}" if tail else "other"
        return BUILD_FAILED, err_phase, err_kind
    except subprocess.TimeoutExpired:
        return BUILD_FAILED, err_phase, "subprocess_timeout"
    except Exception as e:
        return BUILD_FAILED, err_phase, f"exc:{type(e).__name__}"
    finally:
        # Only remove the sentinel if THIS process created it. The
        # FileExistsError path above means another process owns the lock;
        # unconditionally unlinking here would delete its sentinel and let
        # a third concurrent SessionStart `venv --clear` over the in-flight
        # build.
        if we_own_sentinel:
            sentinel.unlink(missing_ok=True)


def _maybe_emit_user_notice(outcome: int, pv: int) -> str | None:
    """Return a one-time user-visible notice when the agentic reviewer is
    in a persistent broken state on this machine, or None if we've already
    shown the notice for this plugin version (or shouldn't show one).

    The marker file is plugin-version-keyed: a future plugin update can
    re-notify if behavior changes (e.g. we ship out-of-process SDK in v3
    and want to tell affected users it's fixed). Failures to write the
    marker degrade to "skip the notice this session" so we don't spam
    every SessionStart on a read-only home dir.

    Currently only HOOK_PY_INCOMPATIBLE qualifies. BUILD_FAILED is
    intentionally excluded — it covers transient causes (network failure,
    pip registry hiccup, in-flight rebuild) where the next session may
    succeed and a permanent notice would mislead.
    """
    if outcome != HOOK_PY_INCOMPATIBLE:
        return None
    try:
        state_dir = Path(_resolve_state_dir())
        marker = state_dir / f".agentic_unavailable_notice_v{pv or 0}"
        if marker.exists():
            return None
        state_dir.mkdir(parents=True, exist_ok=True)
        # Write timestamp + Python version so the marker is self-documenting
        # if a user goes looking. O_EXCL would be racier with no real win
        # (two concurrent SessionStarts both showing the notice once is fine).
        marker.write_text(
            f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} "
            f"py={sys.version_info[0]}.{sys.version_info[1]}\n"
        )
    except OSError:
        return None
    return (
        f"⚠ security-guidance plugin: the cross-file commit reviewer "
        f"(layer 3 of 3 — catches IDOR, auth-bypass, cross-file SSRF) "
        f"is unavailable in this environment. It requires Python ≥3.10, "
        f"but the hook is running on "
        f"{sys.version_info[0]}.{sys.version_info[1]}.\n\n"
        f"Pattern checks and the single-shot LLM diff review are still "
        f"active. To enable the deeper reviewer, install Python 3.10+ "
        f"(e.g. `brew install python` on macOS) and restart Claude Code.\n\n"
        f"This notice is shown once per plugin version. "
        f"See: github.com/anthropics/claude-plugins-official/issues/2071"
    )


if __name__ == "__main__":
    # Tell the harness this is async — venv create + pip install can take
    # 30-60s on a cold cache, well past the default sync hook timeout.
    # SessionStart runs before the user's first prompt; doing this in the
    # background means the first commit-review of the session usually finds
    # the venv ready.
    print(json.dumps({"async": True, "asyncTimeout": 180000}), flush=True)
    t0 = time.perf_counter()
    try:
        outcome, err_phase, err_kind = main()
    except Exception as exc:
        outcome, err_phase, err_kind = (
            BUILD_FAILED, "main", f"exc:{type(exc).__name__}"
        )
    # CC's async-hook registry scans stdout line-by-line after process exit
    # and takes the FIRST non-{"async":...} JSON line as the hook response;
    # its `metrics` key is forwarded to the hook metrics event on the
    # next attachments pass. Must be a single line — the registry splits on
    # \n and json-parses each independently. Values must be bool|number OR
    # short strings (CC accepts string metric values if they're not
    # null). Stay inside the 10-key emit cap.
    metrics: dict[str, object] = {
        "sdk_bootstrap": outcome,
        "sdk_bootstrap_ms": round((time.perf_counter() - t0) * 1000),
    }
    if err_kind:
        # Truncate defensively; categorized values are <40 chars but the
        # `other:<tail>` mode could be longer. err_phase may be empty for
        # pre-venv failures (state_dir.mkdir perm-denied, sentinel O_EXCL
        # raising a non-FileExistsError OSError) — emit as "pre" so the
        # err_kind isn't silently dropped.
        metrics["sdk_bootstrap_phase"] = (err_phase or "pre")[:16]
        metrics["sdk_bootstrap_err"] = err_kind[:96]
    pv = _plugin_version_int()
    if pv:
        metrics["pv"] = pv
    response: dict[str, object] = {"metrics": metrics}
    # One-time user-visible notice when the agentic reviewer is dead on
    # arrival. Uses hookSpecificOutput.additionalContext (SessionStart's
    # supported channel for surfacing text to both the model and the user)
    # plus systemMessage as a belt-and-suspenders. Marker-file-gated so
    # this fires exactly once per plugin version per install — see
    # _maybe_emit_user_notice.
    notice = _maybe_emit_user_notice(outcome, pv)
    if notice:
        response["hookSpecificOutput"] = {
            "hookEventName": "SessionStart",
            "additionalContext": notice,
        }
        response["systemMessage"] = notice
    print(json.dumps(response), flush=True)
