# MCP-Memvid-State-Service

**Single-file AI memory layer with vector search, full-text search, and temporal queries**

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![10 Tools](https://img.shields.io/badge/Tools-10-blue.svg)](#-tool-catalog)
[![Ollama](https://img.shields.io/badge/Embeddings-Ollama-white.svg)](https://ollama.ai/)
[![OpenAI](https://img.shields.io/badge/Embeddings-OpenAI-412991.svg)](https://openai.com/)
[![Local](https://img.shields.io/badge/Embeddings-Local-orange.svg)](#embedding-providers)

[Quick Start](#-quick-start) | [Tool Catalog](#-tool-catalog) | [Embedding Providers](#-embedding-providers) | [Configuration](#-configuration) | [Examples](#-examples)

---

## 🧠 What is this?

An MCP (Model Context Protocol) server wrapping [memvid](https://memvid.com) - a Rust-based memory system that stores everything in a single portable `.mv2` file. Replace Redis for caching, Qdrant/Pinecone for vector search, and SQLite for structured queries—all without external infrastructure.

> Part of the [Claude Code Plugin Marketplace](https://github.com/EricGrill/agents-skills-plugins) ecosystem.

---

## 🚀 Quick Start

**1. Add to Claude Code:**

```json
{
  "mcpServers": {
    "memvid": {
      "command": "npx",
      "args": ["mcp-memvid"],
      "env": {
        "OLLAMA_HOST": "http://localhost:11434"
      }
    }
  }
}
```

**2. Or install and run manually:**

```bash
git clone https://github.com/EricGrill/mcp-memvid-state-service.git
cd mcp-memvid-state-service
npm install && npm run build
node dist/index.js
```

---

## 💡 Why Use MCP-Memvid?

| Feature | Description |
|---------|-------------|
| **Single-file storage** | All data, indices, and metadata in one portable `.mv2` file |
| **No infrastructure** | No Redis, no Postgres, no vector DB cluster to manage |
| **Triple search** | Semantic (vector), lexical (BM25), and temporal queries |
| **Local-first** | Built-in embedding models work offline on Linux/macOS |
| **Ollama support** | Use local LLMs for embeddings without API costs |

---

## 📦 Tool Catalog

| Category | Tools | Description |
|----------|-------|-------------|
| **Storage** | 2 | Store and delete memories (`store_memory`, `delete_capsule`) |
| **Search** | 4 | Vector, keyword, smart, and temporal (`semantic_search`, `text_search`, `smart_search`, `recent_memories`) |
| **Management** | 3 | Capsule lifecycle (`list_capsules`, `create_capsule`, `capsule_info`) |
| **Config** | 1 | View embedding status (`embedding_config`) |

---

## 🔧 All Tools

### Storage

| Tool | Description |
|------|-------------|
| `store_memory` | Store text with title, tags, metadata, and optional embeddings |
| `delete_capsule` | Permanently delete a capsule file (requires confirmation) |

### Search

| Tool | Description |
|------|-------------|
| `semantic_search` | Find by meaning using vector embeddings (HNSW) |
| `text_search` | Find by exact keywords using BM25 ranking |
| `smart_search` | Auto-select best search mode based on query |
| `recent_memories` | Retrieve memories in chronological order |

### Capsule Management

| Tool | Description |
|------|-------------|
| `list_capsules` | List all available memory capsules |
| `create_capsule` | Create a new empty capsule |
| `capsule_info` | Get storage path and existence status |

### Configuration

| Tool | Description |
|------|-------------|
| `embedding_config` | Show current embedding model, Ollama status, API keys |

---

## 🤖 Embedding Providers

| Provider | Setup | Models | Best For |
|----------|-------|--------|----------|
| **Local** | None needed | `bge-small`, `bge-base`, `nomic`, `gte-large` | Offline, privacy-first |
| **Ollama** | `OLLAMA_HOST=http://localhost:11434` | Any via OpenAI API | Local LLMs, no API costs |
| **OpenAI** | `OPENAI_API_KEY=sk-...` | `openai-small`, `openai-large` | Best quality, cloud |

### Ollama Setup

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull an embedding model
ollama pull nomic-embed-text

# Set environment variable
export OLLAMA_HOST=http://localhost:11434
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OLLAMA_HOST` | Ollama server URL | — |
| `OPENAI_API_KEY` | OpenAI API key | — |
| `OPENAI_BASE_URL` | Custom OpenAI-compatible endpoint | — |
| `MEMVID_EMBEDDING_MODEL` | Default embedding model | `bge-small` |
| `XDG_DATA_HOME` | Base storage directory | `~/.local/share` |

### Storage Location

```
$XDG_DATA_HOME/memvid/capsules/
├── agent-context.mv2
├── knowledge-base.mv2
└── session-cache.mv2
```

---

## 📝 Examples

### Store a memory with embeddings

```javascript
store_memory({
  capsule: "knowledge-base",
  text: "The API uses JWT tokens with 24-hour expiry. Refresh tokens last 7 days.",
  title: "Auth Architecture",
  tags: ["api", "security", "jwt"],
  enable_embedding: true,
  embedding_model: "bge-small"
})
```

### Semantic search

```javascript
semantic_search({
  capsule: "knowledge-base",
  query: "how long do authentication tokens last",
  limit: 5
})
```

### Get recent context

```javascript
recent_memories({
  capsule: "agent-context",
  limit: 10
})
```

### Check embedding configuration

```javascript
embedding_config()
// Returns:
// {
//   "defaultModel": "bge-small",
//   "ollamaHost": "http://localhost:11434",
//   "openaiBaseUrl": "http://localhost:11434/v1",
//   ...
// }
```

---

## 🖥️ Platform Support

| Platform | Local Embeddings | Notes |
|----------|------------------|-------|
| Linux x64 | ✅ Yes | Full support |
| macOS ARM64 | ✅ Yes | Full support (Apple Silicon) |
| macOS x64 | ✅ Yes | Full support (Intel) |
| Windows x64 | ❌ No | Use Ollama or OpenAI |

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open a Pull Request

---

## 📜 License

MIT License - see [LICENSE](LICENSE) for details.

---

<p align="center">
  <a href="https://github.com/EricGrill/agents-skills-plugins">
    <img src="https://img.shields.io/badge/Part%20of-Claude%20Code%20Plugin%20Marketplace-blueviolet?style=for-the-badge" alt="Plugin Marketplace">
  </a>
</p>
