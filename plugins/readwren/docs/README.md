# WREN Documentation

This directory contains comprehensive documentation for the WREN Literary Interview Agent.

## Documentation Files

### Core Documentation

**[TECHNICAL_DOCUMENTATION.md](TECHNICAL_DOCUMENTATION.md)**
Complete technical reference covering:
- Architecture overview and design decisions
- LangGraph implementation details
- Redis integration and custom checkpointer
- Multi-agent system with detailed agent descriptions
- Tool implementations and analysis methods
- Prompt engineering strategies
- Data flow and state management
- Configuration and deployment
- Debugging guide and troubleshooting

### Scoring System

**[PROFILE_RUBRIC.md](PROFILE_RUBRIC.md)**
Comprehensive scoring system for all profile metrics:
- Style signature metrics (0-100 scales)
- Prose density, pacing, tone scales
- Worldbuilding and character focus definitions
- Implicit signals (vocabulary, brevity, engagement)
- Interpretation guidelines and examples
- Usage in profile generation

**[RUBRIC_INTEGRATION.md](RUBRIC_INTEGRATION.md)**
Technical guide on how the rubric is used in code:
- Dynamic rubric loading implementation
- Prompt injection mechanism
- Code examples and testing methods
- Benefits of the dynamic approach
- Updating and maintaining the rubric

### Infrastructure

**[REDIS_GUIDE.md](REDIS_GUIDE.md)**
Redis setup and session management:
- Redis Cloud configuration
- Viewing sessions in dashboard
- Using redis-cli for inspection
- Session lifecycle and TTL
- Troubleshooting connection issues
- Python scripts for session management

## Quick Navigation

| Need to... | See... |
|------------|--------|
| Understand the architecture | [TECHNICAL_DOCUMENTATION.md](TECHNICAL_DOCUMENTATION.md) - Architecture Overview |
| Learn about agents | [TECHNICAL_DOCUMENTATION.md](TECHNICAL_DOCUMENTATION.md) - Agents |
| See how tools work | [TECHNICAL_DOCUMENTATION.md](TECHNICAL_DOCUMENTATION.md) - Tools |
| Understand scoring | [PROFILE_RUBRIC.md](PROFILE_RUBRIC.md) |
| Modify rubric scales | [RUBRIC_INTEGRATION.md](RUBRIC_INTEGRATION.md) |
| Set up Redis | [REDIS_GUIDE.md](REDIS_GUIDE.md) |
| Debug issues | [TECHNICAL_DOCUMENTATION.md](TECHNICAL_DOCUMENTATION.md) - Common Issues |

## Documentation Philosophy

The documentation follows these principles:

1. **Technical Depth**: Explains not just what, but how and why
2. **Code Examples**: Real code snippets from the actual implementation
3. **Progressive Detail**: High-level overviews with deep-dive sections
4. **Practical Focus**: Emphasizes actionable information
5. **Cross-Referenced**: Documents link to related sections

## For Developers

If you're building on WREN or adapting it for other domains:

1. Start with [TECHNICAL_DOCUMENTATION.md](TECHNICAL_DOCUMENTATION.md) - Architecture Overview
2. Review the agent implementations in `src/agents/`
3. Understand the tool system in [TECHNICAL_DOCUMENTATION.md](TECHNICAL_DOCUMENTATION.md) - Tools
4. Study the rubric integration for your own scoring system
5. Check out `../examples/example_session/` for real output

## For Users

If you're using WREN to generate literary profiles:

1. See the main [README.md](../README.md) for quick start
2. Check [PROFILE_RUBRIC.md](PROFILE_RUBRIC.md) to understand your scores
3. Review `../examples/example_session/` to see what output looks like
4. Use [REDIS_GUIDE.md](REDIS_GUIDE.md) if you want to view your sessions

## Contributing to Documentation

When updating documentation:

1. Keep code examples synchronized with actual implementation
2. Update all cross-references if file names change
3. Test all command examples before committing
4. Maintain the technical tone (see user rules in project root)
5. Add new sections to this index when creating new docs

---

**Last Updated**: November 2025  
**Project**: [WREN - AI Literary Interview Agent](https://github.com/muratcankoylan/readwren)
