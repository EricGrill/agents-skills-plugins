---
description: Save a durable preference, verified fact, project decision, or technical conclusion to MIndex. Use when the user explicitly asks Claude to remember something for future sessions.
argument-hint: "<fact or decision to remember>"
disable-model-invocation: true
---

# Remember With MIndex Memory

Save `$ARGUMENTS` only when it has durable value beyond the current
conversation.

## Safety Filter

Refuse to store passwords, API keys, access tokens, private keys, authentication
material, or full conversation transcripts. Ask before storing sensitive
personal information.

Do not store temporary discussion, guesses, or claims that have not been
verified. If the requested memory is ambiguous, ask one focused question.

## Procedure

1. Locate MIndex by reading the managed import block in
   `~/.claude/CLAUDE.md`. The imported path ends in `CLAUDE.md`; its parent is
   the memory root.
2. If no valid installation exists, tell the user to run `/mindex:setup`.
3. Search existing memory files before writing. Update the canonical entry
   instead of creating a duplicate.
4. Choose the category:
   - `preferences/`: stable user preferences and working rules
   - `projects/`: project state and decisions
   - `tech/`: verified technical conclusions
   - `daily/`: dated activity summaries
   - `archive/`: inactive or superseded material
5. Preserve valid YAML frontmatter and set `updated` to today's local date.
6. Keep provenance or decision dates when resolving conflicting facts.
7. Use the repository's `.memory.lock` protocol for the complete read-modify-
   verify transaction. Do not only lock index generation.
8. Rebuild and verify:

   ```bash
   python3 "<memory-root>/tools/generate_index.py"
   python3 "<memory-root>/tools/verify.py"
   ```

9. Report the file changed and a one-sentence summary. Never commit or push
   memory unless the user explicitly requests it.
