#!/usr/bin/env python3
"""
ActualCode Web Server
Flask + SocketIO server for real-time agent communication visualization
"""

import asyncio
import json
import os
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import logging

from utils.github_mcp import get_github_mcp
from orchestrator import AssessmentOrchestrator
from utils.monitoring import AgentLogger

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='web_ui', static_url_path='')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Store active sessions
active_sessions = {}


class WebSocketLogger(AgentLogger):
    """Custom logger that emits to websocket"""
    
    def __init__(self, agent_name: str, session_id: str):
        super().__init__(agent_name)
        self.session_id = session_id
    
    def log(self, message: str, level: str = "info"):
        """Emit log to websocket"""
        socketio.emit('agent_log', {
            'session_id': self.session_id,
            'agent': self.agent_name,
            'message': message,
            'level': level,
            'timestamp': datetime.now().isoformat()
        })
        super().log(message, level)


@app.route('/')
def index():
    """Serve React app"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory(app.static_folder, path)


@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'github_token_configured': bool(os.getenv('GITHUB_TOKEN') or os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN')),
        'google_cloud_configured': bool(os.getenv('GOOGLE_CLOUD_PROJECT'))
    })


@app.route('/api/agents')
def get_agents():
    """Get list of agents"""
    agents = [
        {
            'id': 'scanner',
            'name': 'Scanner Agent',
            'description': 'Retrieves repository data from GitHub',
            'icon': '🔍',
            'color': '#4A90E2'
        },
        {
            'id': 'code_analyzer',
            'name': 'Code Analyzer',
            'description': 'Analyzes code structure, patterns, and quality',
            'icon': '💻',
            'color': '#7B68EE'
        },
        {
            'id': 'pr_analyzer',
            'name': 'PR Analyzer',
            'description': 'Analyzes pull requests for common patterns',
            'icon': '🔀',
            'color': '#50C878'
        },
        {
            'id': 'issue_analyzer',
            'name': 'Issue Analyzer',
            'description': 'Analyzes issues and bug reports',
            'icon': '🐛',
            'color': '#FF6B6B'
        },
        {
            'id': 'dependency_analyzer',
            'name': 'Dependency Analyzer',
            'description': 'Analyzes dependencies and tech stack',
            'icon': '📦',
            'color': '#FFA500'
        },
        {
            'id': 'problem_creator',
            'name': 'Problem Creator',
            'description': 'Generates coding assessment problems',
            'icon': '✨',
            'color': '#9B59B6'
        },
        {
            'id': 'qa_validator',
            'name': 'QA Validator',
            'description': 'Validates and scores generated problems',
            'icon': '✅',
            'color': '#2ECC71'
        }
    ]
    return jsonify(agents)


@socketio.on('connect')
def handle_connect():
    """Handle websocket connection"""
    logger.info(f"Client connected: {request.sid}")
    emit('connected', {'session_id': request.sid})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle websocket disconnect"""
    logger.info(f"Client disconnected: {request.sid}")
    if request.sid in active_sessions:
        del active_sessions[request.sid]


@socketio.on('start_generation')
def handle_generation(data):
    """Handle assessment generation request"""
    session_id = request.sid
    
    try:
        repo_url = data.get('repo_url')
        difficulty = data.get('difficulty', 'medium')
        time_limit = data.get('time_limit', 180)
        problem_type = data.get('problem_type', 'feature')
        
        logger.info(f"Starting generation for session {session_id}: {repo_url}")
        
        # Store session
        active_sessions[session_id] = {
            'repo_url': repo_url,
            'status': 'running',
            'start_time': datetime.now().isoformat()
        }
        
        # Run generation in background
        socketio.start_background_task(
            run_generation,
            session_id,
            repo_url,
            difficulty,
            time_limit,
            problem_type
        )
        
        emit('generation_started', {
            'session_id': session_id,
            'repo_url': repo_url
        })
        
    except Exception as e:
        logger.error(f"Error starting generation: {e}")
        emit('error', {
            'message': str(e),
            'type': 'generation_start_error'
        })


def emit_log(session_id, message, agent='System'):
    """Helper to emit log messages to WebSocket"""
    socketio.emit('agent_log', {
        'session_id': session_id,
        'agent': agent,
        'message': message,
        'level': 'info',
        'timestamp': datetime.now().isoformat()
    })

def run_generation(session_id, repo_url, difficulty, time_limit, problem_type):
    """Run the assessment generation process"""
    import sys
    from io import StringIO
    
    old_stdout = sys.stdout  # Save original stdout
    
    # Capture stdout to stream to WebSocket
    class TeeOutput:
        def __init__(self, session_id):
            self.terminal = old_stdout
            self.session_id = session_id
            self.buffer = []
            
        def write(self, message):
            self.terminal.write(message)
            self.terminal.flush()
            if message.strip():
                # Parse agent information from log lines
                agent = 'orchestrator'
                if ' - ' in message:
                    parts = message.split(' - ')
                    if len(parts) >= 2:
                        agent = parts[0].split()[-1] if parts[0].split() else 'orchestrator'
                
                # Emit to WebSocket
                emit_log(self.session_id, message.strip(), agent)
                
        def flush(self):
            self.terminal.flush()
    
    try:
        # Create new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Redirect stdout to capture and stream logs
        tee = TeeOutput(session_id)
        sys.stdout = tee
        
        # Emit status update
        socketio.emit('agent_status', {
            'session_id': session_id,
            'agent': 'scanner',
            'status': 'running',
            'message': 'Fetching repository data...'
        })
        
        socketio.emit('agent_detail', {
            'session_id': session_id,
            'agent': 'scanner',
            'type': 'input',
            'data': {
                'repo_url': repo_url,
                'fetch_issues': True,
                'fetch_prs': True,
                'fetch_commits': True,
                'max_items': 20
            }
        })
        
        # Get GitHub token
        github_token = os.getenv('GITHUB_TOKEN') or os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN')
        
        # Fetch repository data
        github_client = get_github_mcp(github_token)
        repo_data = loop.run_until_complete(
            github_client.fetch_repository_data(
                repo_url=repo_url,
                fetch_issues=True,
                fetch_prs=True,
                fetch_commits=True,
                max_items=20
            )
        )
        
        socketio.emit('agent_detail', {
            'session_id': session_id,
            'agent': 'scanner',
            'type': 'output',
            'data': {
                'repository': repo_data['repository'].get('name', 'N/A'),
                'language': repo_data['repository'].get('language', 'N/A'),
                'total_files': repo_data['codebase']['total_files'],
                'issues_count': len(repo_data['issues']),
                'prs_count': len(repo_data['pull_requests']),
                'commits_count': len(repo_data['commits']),
                'file_extensions': repo_data['codebase'].get('file_extensions', {}),
                'dependencies': repo_data['codebase'].get('dependencies', {})
            }
        })
        
        socketio.emit('agent_status', {
            'session_id': session_id,
            'agent': 'scanner',
            'status': 'complete',
            'message': f"Repository data fetched: {repo_data['codebase']['total_files']} files"
        })
        
        socketio.emit('repo_data', {
            'session_id': session_id,
            'data': {
                'name': repo_data['repository'].get('name', 'N/A'),
                'language': repo_data['repository'].get('language', 'N/A'),
                'files': repo_data['codebase']['total_files'],
                'issues': len(repo_data['issues']),
                'prs': len(repo_data['pull_requests']),
                'commits': len(repo_data['commits'])
            }
        })
        
        # Initialize orchestrator with WebSocket logging
        socketio.emit('agent_status', {
            'session_id': session_id,
            'agent': 'orchestrator',
            'status': 'running',
            'message': 'Starting multi-agent analysis...'
        })
        
        orchestrator = AssessmentOrchestrator()
        
        # Emit agent statuses during analysis
        analysis_agents = ['code_analyzer', 'pr_analyzer', 'issue_analyzer', 'dependency_analyzer']
        for agent in analysis_agents:
            socketio.emit('agent_status', {
                'session_id': session_id,
                'agent': agent,
                'status': 'running',
                'message': f'Analyzing {agent.replace("_", " ")}...'
            })
        
        socketio.emit('agent_detail', {
            'session_id': session_id,
            'agent': 'orchestrator',
            'type': 'input',
            'data': {
                'difficulty': difficulty,
                'time_limit': time_limit,
                'problem_type': problem_type,
                'analysis_mode': 'single-pass (optimized)',
                'agents_activated': analysis_agents
            }
        })
        
        # Generate assessment
        result = loop.run_until_complete(
            orchestrator.generate_assessment(
                github_repo_url=repo_url,
                difficulty=difficulty,
                time_limit=time_limit,
                problem_type=problem_type,
                repo_data=repo_data
            )
        )
        
        # Extract analysis results
        if 'debug' in result and 'analysis_report' in result['debug']:
            analysis_report = result['debug']['analysis_report']
            
            # Emit detailed analysis results for each agent
            for agent in analysis_agents:
                agent_key = agent.replace('_analyzer', '')
                if agent_key in analysis_report:
                    socketio.emit('agent_detail', {
                        'session_id': session_id,
                        'agent': agent,
                        'type': 'output',
                        'data': analysis_report[agent_key]
                    })
        
        # Mark analysis agents as complete
        for agent in analysis_agents:
            socketio.emit('agent_status', {
                'session_id': session_id,
                'agent': agent,
                'status': 'complete',
                'message': 'Analysis complete'
            })
        
        # Problem creation
        socketio.emit('agent_status', {
            'session_id': session_id,
            'agent': 'problem_creator',
            'status': 'running',
            'message': 'Generating assessment problem...'
        })
        
        # Extract problem details
        assessment = result.get('assessment', {})
        problem = assessment.get('problem', {})
        
        socketio.emit('agent_detail', {
            'session_id': session_id,
            'agent': 'problem_creator',
            'type': 'output',
            'data': {
                'title': problem.get('title', 'N/A'),
                'difficulty': problem.get('difficulty', 'N/A'),
                'estimated_time': problem.get('estimated_time', 'N/A'),
                'requirements_count': len(problem.get('requirements', [])),
                'acceptance_criteria_count': len(problem.get('acceptance_criteria', [])),
                'starter_code_files': len(problem.get('starter_code', [])),
                'tech_stack': problem.get('tech_stack', [])
            }
        })
        
        socketio.emit('agent_status', {
            'session_id': session_id,
            'agent': 'problem_creator',
            'status': 'complete',
            'message': 'Problem generated'
        })
        
        # QA Validation
        socketio.emit('agent_status', {
            'session_id': session_id,
            'agent': 'qa_validator',
            'status': 'running',
            'message': 'Validating assessment quality...'
        })
        
        validation = assessment.get('validation', {})
        
        socketio.emit('agent_detail', {
            'session_id': session_id,
            'agent': 'qa_validator',
            'type': 'output',
            'data': {
                'overall_score': validation.get('overall_score', 0),
                'scores': validation.get('scores', {}),
                'passed': validation.get('overall_score', 0) >= 85,
                'iterations': validation.get('iterations', 1),
                'feedback': validation.get('feedback', {})
            }
        })
        
        socketio.emit('agent_status', {
            'session_id': session_id,
            'agent': 'qa_validator',
            'status': 'complete',
            'message': f"Validation complete (Score: {validation.get('overall_score', 0)}/100)"
        })
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"assessment_{timestamp}.json"
        
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        # Emit completion
        socketio.emit('generation_complete', {
            'session_id': session_id,
            'result': result,
            'output_file': output_file
        })
        
        # Update session
        active_sessions[session_id]['status'] = 'complete'
        active_sessions[session_id]['end_time'] = datetime.now().isoformat()
        
    except Exception as e:
        logger.error(f"Error in generation: {e}", exc_info=True)
        socketio.emit('error', {
            'session_id': session_id,
            'message': str(e),
            'type': 'generation_error'
        })
        
        if session_id in active_sessions:
            active_sessions[session_id]['status'] = 'error'
            active_sessions[session_id]['error'] = str(e)
    
    finally:
        # Restore stdout
        sys.stdout = old_stdout
        loop.close()


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))  # Changed to 5001 to avoid macOS AirPlay conflict
    print(f"""
╔═══════════════════════════════════════════════════════════════════╗
║                         ActualCode Web UI                         ║
║                   AI-Powered Assessment Generator                 ║
╚═══════════════════════════════════════════════════════════════════╝

🌐 Server running on http://localhost:{port}
🔌 WebSocket enabled for real-time updates

Press Ctrl+C to stop the server
""")
    socketio.run(app, host='0.0.0.0', port=port, debug=True, allow_unsafe_werkzeug=True)
