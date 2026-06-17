---
description: Install or reconnect MIndex as the user's cross-project Claude Code memory. Use when the user asks to set up, install, initialize, or repair MIndex.
argument-hint: "[optional installation directory]"
disable-model-invocation: true
---

# Set Up MIndex Memory

Install the writable memory repository separately from this plugin. Never store
user memory inside `${CLAUDE_PLUGIN_ROOT}`, because marketplace plugin files are
managed installation artifacts and may be replaced during updates.

## Procedure

1. Choose the destination:
   - Use `$ARGUMENTS` when the user supplied a directory.
   - Otherwise use `~/.claude/mindex`.
2. Expand `~` and resolve the absolute destination path.
3. If the destination is absent, clone:

   ```bash
   git clone https://github.com/li-jin-xuan/mindex.git "<destination>"
   ```

4. If it is already a MIndex checkout, preserve all local memory files. Run
   `git status --short` and do not pull when that could overwrite or conflict
   with local changes.
5. Run:

   ```bash
   python3 "<destination>/tools/install.py"
   python3 "<destination>/tools/generate_index.py"
   python3 "<destination>/tools/verify.py"
   ```

6. On Windows, use `python` when `python3` is unavailable.
7. Report the resolved memory location and verification result.

Do not initialize sample files with personal data. Do not commit or push any
memory without explicit user approval.
