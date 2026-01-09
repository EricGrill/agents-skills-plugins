# WREN Utility Scripts

This directory contains utility scripts for managing and inspecting WREN interview sessions.

## Scripts

### Session Management

**`view_redis_sessions.py`**

Lists all active sessions stored in Redis with metadata.

```bash
python scripts/view_redis_sessions.py
```

**Output**:
```
================================================================================
                             WREN SESSIONS IN REDIS                             
================================================================================

Found 18 active session(s):

Session ID: cli_20251108_145739
--------------------------------------------------------------------------------
  Turn count: 8/12
  Messages: 16
  Status: Complete
  TTL: 22.0 hours remaining
```

**Use when**:
- You want to see all active sessions
- Checking if a session expired
- Monitoring Redis usage
- Finding session IDs for retrieval

---

**`view_session_conversation.py`**

Decodes a Redis checkpoint and displays the full conversation.

```bash
python scripts/view_session_conversation.py <session_id>
```

**Example**:
```bash
python scripts/view_session_conversation.py cli_20251108_145739
```

**Output**: Formatted conversation with turn-by-turn breakdown, including reasoning if available.

**Use when**:
- You need to inspect an active Redis session
- Debugging conversation flow
- Checking what's stored in Redis checkpoints
- Session hasn't been saved to files yet

---

**`view_conversation_log.py`**

Displays a saved conversation log in human-readable format.

```bash
python scripts/view_conversation_log.py <log_file_path>
```

**Example**:
```bash
python scripts/view_conversation_log.py user_profiles/cli_20251108_145739/logs/conversation_20251108_150303.json
```

**Output**: Clean formatted conversation with role labels, turn numbers, and reasoning excerpts.

**Use when**:
- Reviewing completed interviews
- Analyzing conversation patterns
- Sharing interview transcripts
- The session has been saved to user_profiles/

---

**`retrieve_profile.py`**

Retrieves a profile from Redis or demonstrates manual profile creation.

```bash
python scripts/retrieve_profile.py
```

**Features**:
- Connect to Redis and retrieve session data
- Extract profile from checkpoint
- Demonstrates manual profile structure
- Example code for working with profiles programmatically

**Use when**:
- You need to manually extract a profile
- Redis session expired but you want to recreate it
- Learning the profile data structure
- Testing profile generation

## Usage Patterns

### Development Workflow

```bash
# 1. Start an interview
./run_interview.sh

# 2. Check active sessions
python scripts/view_redis_sessions.py

# 3. View conversation in Redis (while in progress)
python scripts/view_session_conversation.py cli_20251108_145739

# 4. After completion, view saved log
python scripts/view_conversation_log.py user_profiles/cli_20251108_145739/logs/conversation_20251108_150303.json
```

### Debugging Session Issues

```bash
# Check if session exists in Redis
python scripts/view_redis_sessions.py | grep <session_id>

# View conversation state
python scripts/view_session_conversation.py <session_id>

# Check saved logs
ls -la user_profiles/<session_id>/logs/
python scripts/view_conversation_log.py user_profiles/<session_id>/logs/*.json
```

### Profile Recovery

```bash
# If Redis session expired but conversation log exists
python scripts/view_conversation_log.py user_profiles/<session_id>/logs/conversation.json

# Extract conversation and regenerate profile
# (Use retrieve_profile.py as a template to write custom recovery script)
```

## Requirements

All scripts require:
- Redis connection (configured in `.env`)
- Python 3.11+
- Dependencies from `requirements.txt`

## Output Format

All scripts use consistent formatting:

- **User messages**: Prefixed with 👤 USER
- **Agent messages**: Prefixed with 🎭 AGENT
- **Reasoning**: Prefixed with 💭 REASONING (if available)
- **Metadata**: Section headers with ═ borders
- **Turn indicators**: Clear turn numbering

## Environment Setup

Scripts automatically load environment variables from `.env`:

```bash
# Required for Redis scripts
REDIS_HOST=your-redis-host.com
REDIS_PORT=17887
REDIS_PASSWORD=your-password
```

If Redis is not configured, scripts will show appropriate error messages.

## Adding New Scripts

When adding new utility scripts:

1. Follow the existing naming convention: `verb_noun.py`
2. Add a detailed docstring at the top
3. Include usage instructions in the script
4. Update this README with a new section
5. Test with both Redis and file-based data sources

## See Also

- [REDIS_GUIDE.md](../docs/REDIS_GUIDE.md): Redis setup and configuration
- [TECHNICAL_DOCUMENTATION.md](../docs/TECHNICAL_DOCUMENTATION.md): System architecture
- [Example Session](../examples/example_session/): Sample outputs

---

**Note**: These are utility scripts for development and inspection. The main interview flow is in `cli_interview.py` at the project root.

