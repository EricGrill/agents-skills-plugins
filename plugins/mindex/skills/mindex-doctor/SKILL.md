---
description: Diagnose MIndex installation, indexing, locking, privacy, and consistency problems. Use when MIndex memory is missing, stale, duplicated, or failing validation.
disable-model-invocation: true
---

# Diagnose MIndex Memory

## Checks

1. Locate the managed MIndex block in `~/.claude/CLAUDE.md`.
2. Confirm the imported `CLAUDE.md`, `INDEX.md`, and maintenance scripts exist.
3. Run `tools/install.py --check`.
4. Run `tools/verify.py`.
5. Confirm `.memory.lock` is ignored by Git. Its existence is normal and does
   not mean the lock is held.
6. Check for untracked or staged files that look like credentials or private
   keys. Do not print their contents.
7. Check whether `INDEX.md` is stale without editing it directly.
8. Report exact failures, then apply non-destructive fixes.

Never delete a lock file to clear a suspected stale lock. Never reset, discard,
commit, or push user memory without explicit approval.
