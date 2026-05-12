# VideoDB

Server-side video and audio perception skill for AI agents: ingest, understand, search, edit, and stream.

**Author:** [VideoDB](https://videodb.io)
**Repository:** https://github.com/video-db/skills
**License:** MIT

## Description

VideoDB Skills gives your AI coding agent one consistent interface to See, Understand, and Act on video and audio — across realtime streams and batch workflows, server-side.

Works with Claude Code, Cursor, Copilot, and other AI agents.

## Skills (1)

- **videodb** — Full video lifecycle: upload, search, edit, transcribe, caption, transcode, capture realtime streams, and return playable HLS links — all via natural language

## Capabilities

| Capability              | What it unlocks                                                               |
| ----------------------- | ----------------------------------------------------------------------------- |
| **Capture**             | Capture desktop screen, mic, and system audio for realtime processing         |
| **Upload**              | Ingest video from YouTube, URLs, RTSP streams, or local files                 |
| **Context**             | Realtime structured context for any RTSP feed or desktop stream               |
| **Search**              | Find exact moments by speech or scene, return playable clips                  |
| **Transcripts**         | Generate clean, timestamped transcripts from any video                        |
| **Subtitles**           | Auto-generate subtitles, then style and burn in or export                     |
| **Edit**                | Trim, merge, clip, overlay text/images/audio, dubbing, and translation        |
| **AI Generate**         | Create images, video, music, sound effects, and voiceovers from text          |
| **Transcode / Reframe** | Change resolution, quality, aspect ratio, and social crops, all server-side   |
| **Stream**              | Instant playable HLS links (built-in CDN) for anything you ingest or generate |

## Installation

Install directly from the source repository:

```bash
npx skills add video-db/skills
```

Or via Claude Code plugin:

```bash
/plugin install videodb@videodb-skills
```

## Setup

```bash
/videodb setup
```

The agent will guide you through:

- Getting your [VideoDB API key](https://console.videodb.io) ($20 free credits, no card required)
- Installing the Python SDK
- Verifying the connection

Set your API key using either method:

```bash
# Recommended: export in terminal
export VIDEO_DB_API_KEY=sk-xxx

# Or add to your project's .env file
VIDEO_DB_API_KEY=sk-xxx
```

> For Cursor, Copilot, and other agents, ask your agent to **"setup videodb"**

## Example Instructions

Ask your agent:

- "Upload https://www.youtube.com/watch?v=... and give me a shareable stream link"
- "Take clips from 10s-30s and 45s-60s and compile them"
- "Generate background music and add it to this clip"
- "Add subtitles with white text on black background"
- "Find every scene showing 'phone close-up' or 'product on screen'"
- "Capture my screen for the next 2 minutes and write a report of what I'm doing"
- "Monitor my IP camera RTSP feed and log an alert with timestamp whenever a person enters the room"

## Requirements

- Python 3.9+
- VideoDB API key ([get one free](https://console.videodb.io))

## Supported Platforms

macOS, Linux, Windows (PowerShell)

## License

MIT

## Links

- **Docs:** [docs.videodb.io](https://docs.videodb.io)
- **Discord:** [Join the community](https://discord.com/invite/py9P639jGz)
- **Source:** [github.com/video-db/skills](https://github.com/video-db/skills)
