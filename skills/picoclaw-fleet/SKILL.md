# PicoClaw Fleet

Orchestrate a fleet of remote PicoClaw workers over SSH for fast, ephemeral one-shot tasks.

## Purpose
Use this skill to deploy PicoClaw to remote machines, dispatch one-shot tasks, fan out work in parallel, and optionally tear workers down after completion.

## Skill Files
- `scripts/deploy.sh` — install/update PicoClaw on a host
- `scripts/dispatch.sh` — run `picoclaw agent -m "TASK"` on a host and return stdout
- `scripts/fleet-status.sh` — check host reachability and install readiness

## 1) Always read fleet config first
Fleet config path:
- `~/.openclaw/workspace/config/picoclaw-fleet.json`

If missing, create it with this default template:

```json
{
  "hosts": [
    {
      "name": "darth",
      "host": "192.168.50.57",
      "user": "eric",
      "arch": "arm64",
      "ssh_key": "~/.ssh/id_rsa"
    }
  ],
  "defaults": {
    "provider": "anthropic",
    "api_key_env": "ANTHROPIC_API_KEY"
  }
}
```

## 2) Deploy PicoClaw to a host
Use `scripts/deploy.sh <host> <user> <arch> [ssh_key]`.

Expected behavior:
- Resolve latest release from `EricGrill/picoclaw` GitHub releases
- Select architecture asset (`amd64`, `arm64`, `riscv64`)
- Install binary remotely to `~/.local/bin/picoclaw`
- Create `~/.picoclaw/.env` with provider + API key env value
- Run `picoclaw onboard`

Required envs before deploy:
- `ANTHROPIC_API_KEY` (default) or whichever env is set by `defaults.api_key_env`
- Optional: `PROVIDER` (defaults to `anthropic`)
- Optional: `API_KEY_ENV` override

## 3) Dispatch one-shot work
Use `scripts/dispatch.sh <host> <user> <task> [timeout_seconds]`.

Behavior:
- SSH into host
- Run `picoclaw agent -m "TASK"`
- Enforce timeout (default 120s)
- Return stdout directly (clean output for inline display)

## 4) Run tasks in parallel across hosts
For multi-task batches, dispatch to multiple hosts in background and wait for all:

```bash
scripts/dispatch.sh 192.168.50.57 eric "summarize logs" 120 > /tmp/darth.out 2>&1 &
scripts/dispatch.sh 192.168.50.58 eric "extract action items" 120 > /tmp/lobot.out 2>&1 &
wait
```

Then print each host output inline.

## 5) Host selection policy
For single tasks:
1. Run `scripts/fleet-status.sh`
2. Prefer reachable hosts where picoclaw is installed
3. Pick least-loaded host when load data exists; otherwise pick first available

If selected host is missing PicoClaw, run deploy first.

## 6) Teardown (optional)
To remove PicoClaw after one-shot jobs:

```bash
ssh -i ~/.ssh/id_rsa eric@HOST 'rm -f ~/.local/bin/picoclaw ~/.picoclaw/.env'
```

Use teardown only when explicitly requested or for strict ephemeral execution workflows.

## Failure handling
- SSH failure: report host as unreachable and continue with other hosts
- Deploy failure on one host: continue dispatching to healthy hosts
- Timeout: return timeout status with partial output if present
- Missing config: create template, then re-run

## Recommended workflow
1. Load/validate fleet config
2. Check health: `scripts/fleet-status.sh`
3. Deploy missing hosts: `scripts/deploy.sh ...`
4. Dispatch task(s): `scripts/dispatch.sh ...`
5. Aggregate outputs and return inline
6. Optional teardown if requested