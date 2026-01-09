#!/bin/bash

# Start script for DeepAgent Food Tour Scanner

echo "========================================="
echo "  DeepAgent Food Tour Scanner"
echo "========================================="
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    echo "Please copy .env.example to .env and add your API keys"
    exit 1
fi

# Create logs directory
mkdir -p logs

# Kill any existing processes on our ports
echo "🧹 Cleaning up existing processes..."
lsof -ti:3001,3002,5001 | xargs kill -9 2>/dev/null || true
sleep 1

# Start the three services
echo ""
echo "Starting services..."
echo ""

# Start Scan Manager (port 3001)
echo "🚀 Starting Scan Manager on port 3001..."
cd "$(dirname "$0")"
nohup npm run start > logs/scan-manager.log 2>&1 &
SCAN_PID=$!

# Start Dashboard Server (port 3002)
echo "📊 Starting Dashboard Server on port 3002..."
nohup npm run dashboard-server > logs/dashboard-server.log 2>&1 &
DASHBOARD_PID=$!

# Start DeepAgent API (port 5001)
echo "🧠 Starting DeepAgent API on port 5001..."
nohup python3 -u src/deepagent-api.py > logs/deepagent-api.log 2>&1 &
DEEPAGENT_PID=$!

# Wait a moment for processes to start
sleep 3

# Check if processes are still running
if ! kill -0 $SCAN_PID 2>/dev/null; then
    echo "❌ Scan Manager failed to start. Check logs/scan-manager.log"
fi
if ! kill -0 $DASHBOARD_PID 2>/dev/null; then
    echo "❌ Dashboard Server failed to start. Check logs/dashboard-server.log"
fi
if ! kill -0 $DEEPAGENT_PID 2>/dev/null; then
    echo "❌ DeepAgent API failed to start. Check logs/deepagent-api.log"
    echo "   Common issues:"
    echo "   - Missing API keys in .env file (OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.)"
    echo "   - Missing Python dependencies (run: pip3 install -r requirements.txt)"
fi

echo ""
echo "========================================="
echo "  All services started!"
echo "========================================="
echo ""
echo "📍 Scan Manager:    http://localhost:3001"
echo "📊 Dashboard Server: http://localhost:3002"
echo "🧠 DeepAgent API:    http://localhost:5001"
echo ""
echo "Logs are available in the logs/ directory"
echo "  tail -f logs/scan-manager.log"
echo "  tail -f logs/dashboard-server.log"
echo "  tail -f logs/deepagent-api.log"
echo ""
echo "Process IDs:"
echo "  Scan Manager: $SCAN_PID"
echo "  Dashboard:    $DASHBOARD_PID"
echo "  DeepAgent:    $DEEPAGENT_PID"
echo ""
echo "To stop all services, press Ctrl+C or run:"
echo "  kill $SCAN_PID $DASHBOARD_PID $DEEPAGENT_PID"
echo ""
echo "========================================="

# Wait for user interrupt
wait

