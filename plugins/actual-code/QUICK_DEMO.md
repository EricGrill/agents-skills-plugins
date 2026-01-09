# ActualCode Web UI - Quick Demo Guide

## 🚀 Starting the Server

### Method 1: Startup Script
```bash
cd /Users/muratcankoylan/ActualCode/hackathon_code
./start_web_ui.sh
```

### Method 2: Manual Start
```bash
cd /Users/muratcankoylan/ActualCode/hackathon_code
source venv/bin/activate
python3 web_server.py
```

The server will start on **http://localhost:5001**

## 🎯 Using the Web UI

### 1. Open Browser
Navigate to: **http://localhost:5001**

### 2. Enter Repository Details
In the Configuration panel:
- **Repository**: Enter a GitHub repo URL (e.g., `krutarthh/example-chat-app`)
- **Difficulty**: Choose Easy/Medium/Hard/Expert
- **Problem Type**: Feature/Bug-fix/Refactor/Optimization
- **Time Limit**: 60-240 minutes

### 3. Generate Assessment
Click the **"🚀 Generate Assessment"** button

### 4. Watch the Magic ✨
You'll see in real-time:
- **Scanner Agent** 🔍 - Fetching repository data
- **Code Analyzer** 💻 - Analyzing code structure
- **PR Analyzer** 🔀 - Reviewing pull requests
- **Issue Analyzer** 🐛 - Examining issues
- **Dependency Analyzer** 📦 - Checking tech stack
- **Problem Creator** ✨ - Generating the problem
- **QA Validator** ✅ - Validating quality (85+ score threshold)

### 5. View Results
- See the generated assessment problem
- Check QA validation scores
- Download full JSON results

## 🎭 Demo Tips for Judges

### Highlight These Features:
1. **Multi-Agent Coordination**: Point out all 7 agents working together
2. **Real-time Updates**: Show the live activity log streaming
3. **Quality Assurance**: Demonstrate the QA validator scoring system
4. **Agent Communication**: Explain the A2A protocol in action
5. **Beautiful Visualization**: Show the sleek, modern interface

### Best Repositories to Demo:
- `krutarthh/example-chat-app` - Good for medium difficulty
- Any small React/Node.js project - Fast generation
- Projects with issues/PRs - Shows full analysis capability

### Talking Points:
- "This is a multi-agent AI system with 7 specialized agents"
- "Each agent uses Google Gemini AI for intelligent analysis"
- "Agents communicate through a structured A2A protocol"
- "Real-time WebSocket updates show agent coordination"
- "QA validation ensures high-quality assessments (85+ score)"

## ⚡ Quick Test

Want to test if everything works? Try this:

```bash
# In the hackathon_code directory
python3 test_web_server.py
```

This will:
1. Start the server
2. Test the health endpoint
3. Verify configuration
4. Report results

## 🛠️ Troubleshooting

### Server Won't Start
**Problem**: `ModuleNotFoundError: No module named 'flask'`
**Solution**:
```bash
source venv/bin/activate
pip install flask flask-cors flask-socketio python-socketio eventlet
```

### Can't Connect in Browser
**Problem**: Connection refused
**Solution**: 
- Make sure server is running (check terminal)
- Try http://127.0.0.1:5001 instead
- Check firewall settings

### Port 5000 Already in Use (macOS)
**Problem**: "Address already in use" error
**Solution**: Port 5001 is now default (AirPlay uses 5000 on macOS)
- Server now uses port 5001 by default
- Or disable AirPlay Receiver: System Preferences → General → AirDrop & Handoff

### Agents Not Running
**Problem**: Generation starts but agents don't activate
**Solution**: Check environment variables:
```bash
echo $GITHUB_TOKEN
echo $GOOGLE_CLOUD_PROJECT
```

### Slow Generation
**Normal**: First run takes 2-3 minutes
**Expected Flow**:
- Scanner: ~10 seconds
- Analysis (4 agents): ~60-90 seconds
- Problem Creation: ~30-45 seconds
- QA Validation: ~20-30 seconds

## 📱 What You'll See

### Initial Screen
- Header with "ActualCode" logo
- Configuration form (left)
- Agent dashboard (right) - all agents in "pending" state
- Empty activity log

### During Generation
- Agents turn **orange** (running) with pulsing animation
- Activity log fills with real-time messages
- Repository data appears after scanning
- Agents turn **green** (complete) when done

### After Completion
- All agents marked complete (green)
- Full assessment displayed
- QA scores shown (Feasibility, Quality, Technical, Educational)
- Download button enabled

## 🎨 UI Features

### Color Coding
- **Pending**: Gray - waiting to start
- **Running**: Orange - actively working (animated pulse)
- **Complete**: Green - finished successfully
- **Error**: Red - something went wrong

### Real-time Updates
- WebSocket connection (see status in top-right)
- Activity log auto-scrolls
- Agent cards update instantly
- Progress flows from top to bottom

### Professional Design
- Dark theme (easy on eyes during demos)
- Smooth animations (60 FPS)
- Responsive layout (works on different screen sizes)
- Modern typography (Inter font)

## 🎬 Perfect Demo Flow

1. **Start**: "This is ActualCode, an AI-powered assessment generator"
2. **Show UI**: "Modern web interface with real-time agent monitoring"
3. **Enter Repo**: "Let's analyze this GitHub repository"
4. **Click Generate**: "Watch as 7 AI agents work together"
5. **Show Agents**: "Each agent has a specialized role"
6. **Show Log**: "Real-time communication between agents"
7. **Show Results**: "High-quality assessment generated automatically"
8. **Show Scores**: "QA validation ensures quality (85+ threshold)"
9. **Download**: "Complete JSON ready for use"

## 💡 Why This Impresses Judges

### Technical Excellence
- Multi-agent AI orchestration
- Real-time WebSocket communication
- Google Gemini AI integration
- Structured agent-to-agent protocol

### User Experience
- Beautiful, modern interface
- Real-time visibility into AI processes
- Transparent agent operations
- Professional design quality

### Practical Value
- Solves real hiring/assessment problem
- Scalable architecture
- Production-ready code
- Complete documentation

---

**Ready to wow the judges?** 🚀

Start the server and open http://localhost:5001!
