# Project Development Methodology

Design and build LLM-powered projects from ideation through deployment.

## Overview

This skill covers the methodology for identifying tasks suited to LLM processing, designing effective project architectures, and iterating rapidly using agent-assisted development. The principles apply whether building batch processing pipelines, multi-agent research systems, or interactive applications.

## Contents

```
project-development/
├── SKILL.md                              # Main skill instructions
├── README.md                             # This file
├── references/
│   ├── case-studies.md                   # Karpathy, Vercel, Manus case studies
│   └── pipeline-patterns.md              # Detailed pipeline architecture patterns
└── scripts/
    └── pipeline_template.py              # Template for LLM batch processing
```

## Key Concepts

### Task-Model Fit Recognition

Before building automation, validate that the task is well-suited for LLM processing:

| LLM-Suited | LLM-Unsuited |
|------------|--------------|
| Synthesis across sources | Precise computation |
| Subjective judgment with rubrics | Real-time requirements |
| Error-tolerant batch processing | Perfect accuracy needs |
| Natural language output | Deterministic output |

### Pipeline Architecture

The canonical pipeline structure:

```
acquire → prepare → process → parse → render
```

- **Acquire**: Fetch raw data (deterministic)
- **Prepare**: Generate prompts (deterministic)
- **Process**: Execute LLM calls (non-deterministic, expensive)
- **Parse**: Extract structured data (deterministic)
- **Render**: Generate outputs (deterministic)

Only the Process stage involves LLM calls. All others can be debugged and iterated independently.

### File System as State Machine

Use file existence to track pipeline state:

```
data/{batch}/{item}/
├── raw.json         # acquire complete
├── prompt.md        # prepare complete
├── response.md      # process complete
└── parsed.json      # parse complete
```

To re-run a stage: delete its output file. Natural idempotency without complex state management.

### Structured Output Design

Prompts must specify exact format for reliable parsing:
- Section markers for regex extraction
- Format examples showing expected output
- Rationale disclosure ("I will parse this programmatically")
- Constrained values (score ranges, enumerated options)

## When to Use This Skill

- Starting a new project that might benefit from LLM processing
- Evaluating whether a task fits LLM capabilities
- Designing batch processing or analysis pipelines
- Choosing between single-agent and multi-agent approaches
- Estimating costs and timelines

## Quick Reference

### Development Process

1. **Manual prototype**: Test one example with target model
2. **Agent-assisted build**: Use agents for rapid implementation
3. **Stage-by-stage testing**: Verify each stage independently
4. **Cost estimation**: Track tokens and costs from the start

### Architectural Principles

- Start minimal, add complexity only when proven necessary
- File system for state management and debugging
- Parallel execution for LLM calls
- Robust parsing that handles variations

## Related Skills

- `tool-design` - Tools for agent systems within pipelines
- `multi-agent-patterns` - When to use multiple agents
- `evaluation` - Evaluating pipeline outputs
- `context-compression` - Managing long contexts

## References

- [SKILL.md](./SKILL.md) - Full skill instructions
- [Case Studies](./references/case-studies.md) - Production examples
- [Pipeline Patterns](./references/pipeline-patterns.md) - Detailed patterns

## Version

- **Created**: 2025-12-25
- **Last Updated**: 2025-12-25
- **Version**: 1.0.0

