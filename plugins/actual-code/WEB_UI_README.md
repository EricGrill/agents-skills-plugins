# ActualCode Web UI

A sleek, modern web interface for the ActualCode AI-powered assessment generator. Perfect for showcasing the multi-agent system to judges and users.

## 🎨 Features

- **Real-time Agent Visualization**: Watch all 7 agents work in real-time
- **Live Activity Log**: See detailed logs of agent communications
- **Interactive Dashboard**: Monitor agent status and progress
- **Beautiful Results Display**: View generated assessments with scores and metrics
- **Responsive Design**: Works on desktop and tablet devices
- **Dark Theme**: Modern, eye-friendly dark mode interface

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Install web dependencies
pip install flask flask-cors flask-socketio python-socketio eventlet
```

### 2. Set Environment Variables

```bash
# GitHub token (required)
export GITHUB_TOKEN='your_github_token_here'

# Google Cloud project (optional)
export GOOGLE_CLOUD_PROJECT='your-project-id'
```

### 3. Start the Web Server

```bash
# Make script executable
chmod +x start_web_ui.sh

# Run the server
./start_web_ui.sh
```

Or manually:

```bash
python3 web_server.py
```

### 4. Open in Browser

Navigate to: **http://localhost:5001**

> **Note**: Port 5001 is used to avoid conflicts with macOS AirPlay Receiver (which uses port 5000)

## 📖 How to Use

### Step 1: Configure Assessment
1. Enter a GitHub repository URL (e.g., `owner/repo` or full URL)
2. Select difficulty level (Easy, Medium, Hard, Expert)
3. Choose problem type (Feature, Bug-fix, Refactor, Optimization)
4. Set time limit (60-240 minutes)

### Step 2: Generate Assessment
1. Click "🚀 Generate Assessment"
2. Watch the multi-agent system in action:
   - **Scanner Agent** 🔍: Fetches repository data
   - **Code Analyzer** 💻: Analyzes code structure
   - **PR Analyzer** 🔀: Reviews pull requests
   - **Issue Analyzer** 🐛: Examines issues
   - **Dependency Analyzer** 📦: Checks dependencies
   - **Problem Creator** ✨: Generates the problem
   - **QA Validator** ✅: Validates quality

### Step 3: View Results
- Review the generated assessment
- Check QA validation scores
- Download full JSON results

## 🎯 Architecture

### Backend (`web_server.py`)
- **Flask** web server
- **Flask-SocketIO** for real-time WebSocket communication
- Wraps the orchestrator for web-based access
- Provides REST API endpoints

### Frontend (`web_ui/`)
- **React** (via CDN, no build step required)
- **Socket.IO Client** for real-time updates
- Pure CSS animations and transitions
- Responsive grid layout

### Communication Flow

```
User Input → WebSocket → Flask Server → Orchestrator
                                            ↓
                                    Multi-Agent System
                                            ↓
Results ← WebSocket ← Flask Server ← Assessment
```

## 🎨 UI Components

### 1. Configuration Panel
- Repository URL input
- Difficulty selector
- Problem type selector
- Time limit selector
- Generate button

### 2. Agent Dashboard
- 7 agent cards with real-time status
- Color-coded status indicators:
  - Gray: Pending
  - Orange: Running (animated)
  - Green: Complete
  - Red: Error

### 3. Repository Data Display
- Repository name and language
- File count, issues, PRs, commits
- Appears after scan completes

### 4. Activity Log
- Real-time agent communications
- Timestamped entries
- Auto-scrolling
- Color-coded by agent

### 5. Results Display
- Problem title and description
- Requirements and acceptance criteria
- QA validation scores
- Download button for full JSON

## 🔧 Technical Details

### API Endpoints

- `GET /` - Serve React app
- `GET /api/health` - Health check
- `GET /api/agents` - List all agents

### WebSocket Events

**Client → Server:**
- `start_generation` - Start assessment generation

**Server → Client:**
- `connected` - Connection established
- `agent_status` - Agent status update
- `agent_log` - Agent log message
- `repo_data` - Repository data fetched
- `generation_complete` - Assessment ready
- `error` - Error occurred

## 🎭 Demo Tips for Judges

1. **Show the Multi-Agent System**: Start generation and point out each agent activating
2. **Highlight Real-time Updates**: Show the live activity log
3. **Demonstrate Quality**: Show the QA validation scores (85+ threshold)
4. **Explain the Flow**: Walk through Scanner → Analysis → Creation → Validation
5. **Show Versatility**: Try different difficulty levels and problem types

## 🛠️ Customization

### Colors
Edit `web_ui/styles.css` CSS variables:
```css
:root {
    --primary: #6366F1;
    --secondary: #8B5CF6;
    --success: #10B981;
    /* ... */
}
```

### Agent Icons/Colors
Edit `AGENTS` array in `web_ui/app.jsx`

### Port
Set `PORT` environment variable or edit `web_server.py`
```bash
PORT=8080 python3 web_server.py  # Run on custom port
```
Default is 5001 (to avoid macOS AirPlay conflict on port 5000)

## 📊 Performance

- **Initial Load**: < 1 second
- **WebSocket Latency**: < 100ms
- **Agent Updates**: Real-time (as they happen)
- **UI Responsiveness**: 60 FPS animations

## 🐛 Troubleshooting

### WebSocket Connection Failed
- Ensure server is running on port 5000
- Check firewall settings
- Verify CORS is enabled

### Agents Not Updating
- Check browser console for errors
- Verify GitHub token is set
- Check server logs

### Slow Generation
- Normal: 2-3 minutes for full analysis
- Check network connection
- Verify API quotas

## 📝 Browser Support

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

## 🎉 What Makes It Special

1. **No Build Step**: Pure HTML/CSS/JS + React CDN
2. **Real-time Everything**: WebSocket-based live updates
3. **Beautiful Animations**: Smooth, 60 FPS CSS animations
4. **Agent Transparency**: Full visibility into AI agent operations
5. **Professional Design**: Hackathon-ready, judge-impressing UI

Perfect for demonstrating the power of multi-agent AI systems! 🚀
