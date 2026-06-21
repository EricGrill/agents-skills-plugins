---
description: Search MIndex for relevant long-term preferences, project facts, decisions, and technical notes. Use when the user asks what Claude remembers or requests information from prior sessions.
argument-hint: "<topic to recall>"
disable-model-invocation: true
---

# Recall From MIndex Memory

Retrieve memory relevant to `$ARGUMENTS`.

## Procedure

1. Locate the memory root from the MIndex managed import in
   `~/.claude/CLAUDE.md`.
2. If MIndex is not installed, say so and suggest `/mindex:setup`.
3. Read `INDEX.md` first.
4. Search titles and paths before opening detailed files. Use `rg` when
   available and a platform-appropriate text search otherwise.
5. Open only the smallest set of relevant files.
6. Distinguish recorded facts from current inference. Include each source file
   path in the answer.
7. If entries conflict, prefer neither silently. State the conflict and compare
   their `updated` dates and provenance.
8. Do not reveal unrelated private memory.
