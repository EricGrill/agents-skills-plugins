#!/bin/bash

# Watch all logs in real-time

echo "========================================="
echo "  Watching DeepAgent Logs"
echo "========================================="
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Check if logs directory exists
if [ ! -d "logs" ]; then
    echo "❌ Logs directory not found"
    exit 1
fi

# Create log files if they don't exist
touch logs/scan-manager.log
touch logs/dashboard-server.log
touch logs/deepagent-api.log

# Watch all logs
tail -f logs/scan-manager.log logs/dashboard-server.log logs/deepagent-api.log

