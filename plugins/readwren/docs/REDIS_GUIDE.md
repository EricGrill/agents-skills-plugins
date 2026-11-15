# Redis Session Management Guide

## Overview

Yes, WREN uses Redis Cloud for persistent session storage. All interview state (messages, turn count, analysis) is stored in Redis with 24-hour TTL.

## Your Redis Configuration

Configure in your `.env` file:
```bash
REDIS_HOST=your-redis-instance.redis-cloud.com
REDIS_PORT=17887
REDIS_PASSWORD=your-redis-password-here
```

**Important**: Never commit your actual Redis credentials to git. Always use environment variables.

## Viewing Sessions in Redis Cloud Dashboard

### 1. Access the Web Interface

1. Go to: https://app.redislabs.com/
2. Log in with your Redis Cloud account
3. Navigate to your database

### 2. Use the Browser Tool

In the Redis Cloud dashboard:
- Click on your database
- Go to "Browser" tab
- You'll see all keys in your database

### 3. Search for Session Keys

All WREN sessions are prefixed with:
```
langgraph:checkpoint:{session_id}:*
```

Example keys:
```
langgraph:checkpoint:cli_20251108_145739:latest
langgraph:checkpoint:cli_20251108_145739:checkpoint_id_123
```

## Viewing Sessions via redis-cli

### Connect to Redis

```bash
redis-cli -u redis://default:YOUR_PASSWORD@your-redis-instance.redis-cloud.com:17887
```

Replace `YOUR_PASSWORD` and `your-redis-instance.redis-cloud.com` with your actual credentials from `.env`.

### List All Sessions

```bash
# List all checkpoint keys
KEYS langgraph:checkpoint:*

# Count total sessions
KEYS langgraph:checkpoint:* | wc -l

# List just session IDs (unique)
KEYS langgraph:checkpoint:* | cut -d: -f3 | sort -u
```

### View Specific Session

```bash
# Get latest state for a session
GET langgraph:checkpoint:cli_20251108_145739:latest

# Check TTL (time to live)
TTL langgraph:checkpoint:cli_20251108_145739:latest

# See all keys for a session
KEYS langgraph:checkpoint:cli_20251108_145739:*
```

### Inspect Session Data

The data is stored as pickled Python objects, so it won't be human-readable in redis-cli. To inspect it properly:

```python
import redis
import pickle
import os
from dotenv import load_dotenv

load_dotenv()

# Connect using environment variables
r = redis.Redis(
    host=os.getenv('REDIS_HOST'),
    port=int(os.getenv('REDIS_PORT')),
    password=os.getenv('REDIS_PASSWORD'),
    decode_responses=False  # Important for pickle
)

# Get session
session_id = "cli_20251108_145739"
key = f"langgraph:checkpoint:{session_id}:latest"
data = r.get(key)

if data:
    state = pickle.loads(data)
    checkpoint = state.get('checkpoint', {})
    
    print(f"Turn count: {checkpoint.get('turn_count', 0)}")
    print(f"Messages: {len(checkpoint.get('messages', []))}")
    print(f"Complete: {checkpoint.get('is_complete', False)}")
else:
    print("Session not found or expired")
```

## Using WREN's Built-in Scripts

WREN includes utility scripts to view sessions without manually connecting to Redis:

```bash
# List all active sessions
python scripts/view_redis_sessions.py

# View conversation from Redis checkpoint
python scripts/view_session_conversation.py cli_20251108_145739

# View saved conversation log
python scripts/view_conversation_log.py user_profiles/cli_20251108_145739/logs/conversation.json
```

## Session Lifecycle

### 1. Session Creation

When you start an interview:
```bash
./run_interview.sh
```

WREN creates a new session with ID `cli_TIMESTAMP`.

### 2. During Interview

After each turn:
- State is updated in memory
- LangGraph automatically persists to Redis
- TTL is refreshed to 24 hours

### 3. After Completion

When interview ends:
- Final state saved to Redis
- Conversation log saved to `user_profiles/{session_id}/logs/`
- Profile saved to `user_profiles/{session_id}/profiles/`
- Redis session expires after 24 hours (but files remain)

## Session Data Structure

Each session stores:

```python
{
    "checkpoint": {
        "messages": [HumanMessage, AIMessage, ...],
        "turn_count": 8,
        "is_complete": True,
        "current_analysis": {
            "vocabulary_richness": 0.95,
            "response_brevity": 0.2,
            "engagement_index": 0.95
        },
        "profile_data": {...}
    },
    "metadata": {
        "timestamp": "2025-11-08T15:03:24",
        "version": "1.0"
    },
    "config": {...}
}
```

## TTL (Time To Live)

- **Default TTL**: 24 hours
- **Purpose**: Automatic cleanup of old sessions
- **What happens**: After 24 hours, Redis automatically deletes the session
- **Impact**: You can't resume an interview after 24 hours

**Note**: Even if Redis session expires, your conversation logs and profiles remain in `user_profiles/` permanently.

## Redis Storage Details

### Memory Usage

- Each session: ~2-10 KB (depends on message length)
- 100 sessions: ~200 KB - 1 MB
- Pickled format is compact

### Key Naming Convention

```
langgraph:checkpoint:{session_id}:{checkpoint_id}
```

Examples:
- `langgraph:checkpoint:cli_20251108_145739:latest` - Most recent state
- `langgraph:checkpoint:cli_20251108_145739:abc123` - Specific checkpoint

## Troubleshooting

### Can't Connect to Redis

**Check credentials**:
```bash
redis-cli -u redis://default:YOUR_PASSWORD@your-host.redis-cloud.com:17887 PING
```

Should return: `PONG`

**Common issues**:
- Wrong password in `.env`
- Firewall blocking port 17887
- Redis instance is down

### Session Not Found

**Possible reasons**:
1. TTL expired (24+ hours old)
2. Wrong session ID
3. Redis was cleared/reset

**Solution**: Check `user_profiles/` for permanent logs.

### "Pickle Error" When Loading

**Cause**: Incompatible Python versions or corrupted data

**Solution**: Use the same Python version that created the session.

## Security Best Practices

1. ✅ **Always** use `.env` for credentials
2. ✅ **Never** commit `.env` to git
3. ✅ **Rotate** Redis password periodically
4. ✅ **Use** Redis Cloud's built-in security features
5. ✅ **Limit** access to trusted IPs if possible

## Redis Cloud Setup

If you don't have Redis Cloud configured:

1. Sign up at https://redis.com/try-free/
2. Create a new database (free tier available)
3. Get connection details from dashboard
4. Add to `.env`:
   ```bash
   REDIS_HOST=your-instance.redis-cloud.com
   REDIS_PORT=17887
   REDIS_PASSWORD=your-password-here
   ```

## Running Without Redis

WREN can run without Redis using in-memory storage:

```bash
# Just don't configure Redis in .env
# Or set use_redis=False in code
```

**Limitations**:
- Sessions lost on restart
- Can't resume interrupted interviews
- No multi-device support

---

**For more details**, see:
- [TECHNICAL_DOCUMENTATION.md](TECHNICAL_DOCUMENTATION.md) - Redis integration details
- [../scripts/README.md](../scripts/README.md) - Utility scripts documentation

