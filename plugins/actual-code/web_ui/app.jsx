const { useState, useEffect, useRef } = React;

// Agent definitions
const AGENTS = [
    {
        id: 'scanner',
        name: 'Scanner Agent',
        description: 'Retrieves repository data from GitHub',
        icon: '🔍',
        color: '#4A90E2'
    },
    {
        id: 'code_analyzer',
        name: 'Code Analyzer',
        description: 'Analyzes code structure, patterns, and quality',
        icon: '💻',
        color: '#7B68EE'
    },
    {
        id: 'pr_analyzer',
        name: 'PR Analyzer',
        description: 'Analyzes pull requests for common patterns',
        icon: '🔀',
        color: '#50C878'
    },
    {
        id: 'issue_analyzer',
        name: 'Issue Analyzer',
        description: 'Analyzes issues and bug reports',
        icon: '🐛',
        color: '#FF6B6B'
    },
    {
        id: 'dependency_analyzer',
        name: 'Dependency Analyzer',
        description: 'Analyzes dependencies and tech stack',
        icon: '📦',
        color: '#FFA500'
    },
    {
        id: 'problem_creator',
        name: 'Problem Creator',
        description: 'Generates coding assessment problems',
        icon: '✨',
        color: '#9B59B6'
    },
    {
        id: 'qa_validator',
        name: 'QA Validator',
        description: 'Validates and scores generated problems',
        icon: '✅',
        color: '#2ECC71'
    }
];

function App() {
    const [connected, setConnected] = useState(false);
    const [repoUrl, setRepoUrl] = useState('');
    const [difficulty, setDifficulty] = useState('medium');
    const [problemType, setProblemType] = useState('feature');
    const [timeLimit, setTimeLimit] = useState(180);
    const [isGenerating, setIsGenerating] = useState(false);
    const [agentStatuses, setAgentStatuses] = useState({});
    const [agentDetails, setAgentDetails] = useState({});
    const [activityLog, setActivityLog] = useState([]);
    const [repoData, setRepoData] = useState(null);
    const [result, setResult] = useState(null);
    const [sessionId, setSessionId] = useState(null);
    const [activeView, setActiveView] = useState('agents'); // agents, architecture, a2a, prompts
    const [a2aMessages, setA2AMessages] = useState([]);
    
    const socketRef = useRef(null);
    const logEndRef = useRef(null);

    // Initialize Socket.IO
    useEffect(() => {
        const socket = io('http://localhost:5001');  // Changed to port 5001
        socketRef.current = socket;

        socket.on('connect', () => {
            setConnected(true);
            addLog('System', 'Connected to ActualCode server', 'info');
        });

        socket.on('disconnect', () => {
            setConnected(false);
            addLog('System', 'Disconnected from server', 'error');
        });

        socket.on('connected', (data) => {
            setSessionId(data.session_id);
        });

        socket.on('generation_started', (data) => {
            addLog('System', `Assessment generation started for ${data.repo_url}`, 'info');
        });

        socket.on('agent_status', (data) => {
            setAgentStatuses(prev => ({
                ...prev,
                [data.agent]: {
                    status: data.status,
                    message: data.message
                }
            }));
            addLog(data.agent, data.message, data.status);
        });

        socket.on('agent_log', (data) => {
            addLog(data.agent, data.message, data.level);
            
            // Parse log messages to update agent status dynamically
            const msg = data.message.toLowerCase();
            
            // Detect when agents start
            if (msg.includes('starting') || msg.includes('running agent')) {
                const agentName = data.agent.toLowerCase().replace(/\s+/g, '_');
                setAgentStatuses(prev => ({
                    ...prev,
                    [agentName]: {
                        status: 'running',
                        message: 'Processing...'
                    }
                }));
            }
            
            // Detect when agents complete
            if (msg.includes('completed successfully') || msg.includes('complete')) {
                const agentName = data.agent.toLowerCase().replace(/\s+/g, '_');
                setAgentStatuses(prev => ({
                    ...prev,
                    [agentName]: {
                        status: 'complete',
                        message: 'Completed'
                    }
                }));
            }
        });

        socket.on('agent_detail', (data) => {
            setAgentDetails(prev => ({
                ...prev,
                [data.agent]: {
                    ...prev[data.agent],
                    [data.type]: data.data
                }
            }));
            
            // Track A2A messages
            if (data.type === 'output' || data.type === 'input') {
                setA2AMessages(prev => [...prev, {
                    timestamp: new Date().toISOString(),
                    from: data.type === 'output' ? data.agent : 'orchestrator',
                    to: data.type === 'input' ? data.agent : 'orchestrator',
                    type: data.type,
                    data: data.data
                }]);
            }
            
            // Log detailed info
            const dataStr = JSON.stringify(data.data, null, 2);
            addLog(data.agent, `${data.type.toUpperCase()}: ${dataStr}`, 'detail');
        });

        socket.on('repo_data', (data) => {
            setRepoData(data.data);
            addLog('Scanner', `Repository analyzed: ${data.data.name}`, 'complete');
        });

        socket.on('generation_complete', (data) => {
            setResult(data.result);
            setIsGenerating(false);
            addLog('System', 'Assessment generation complete! 🎉', 'complete');
        });

        socket.on('error', (data) => {
            addLog('System', `Error: ${data.message}`, 'error');
            setIsGenerating(false);
        });

        return () => {
            socket.disconnect();
        };
    }, []);

    // Auto-scroll activity log
    useEffect(() => {
        logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [activityLog]);

    const addLog = (agent, message, level = 'info') => {
        const timestamp = new Date().toLocaleTimeString();
        setActivityLog(prev => [...prev, { agent, message, level, timestamp }]);
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        
        if (!repoUrl.trim()) {
            addLog('System', 'Please enter a repository URL', 'error');
            return;
        }

        setIsGenerating(true);
        setResult(null);
        setRepoData(null);
        setAgentStatuses({});
        setAgentDetails({});
        setActivityLog([]);
        setA2AMessages([]);

        socketRef.current.emit('start_generation', {
            repo_url: repoUrl,
            difficulty,
            time_limit: parseInt(timeLimit),
            problem_type: problemType
        });
    };

    const downloadResult = () => {
        if (!result) return;
        
        const dataStr = JSON.stringify(result, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `assessment_${new Date().getTime()}.json`;
        link.click();
        URL.revokeObjectURL(url);
    };

    return (
        <div className="app">
            <ConnectionStatus connected={connected} />
            
            <header className="header">
                <h1 className="logo">ActualCode</h1>
                <p className="tagline">AI-Powered Assessment Generator</p>
                <p className="subtitle">Multi-Agent Orchestration System</p>
            </header>

            <div className="main-container">
                <div className="left-column">
                    <InputForm
                        repoUrl={repoUrl}
                        setRepoUrl={setRepoUrl}
                        difficulty={difficulty}
                        setDifficulty={setDifficulty}
                        problemType={problemType}
                        setProblemType={setProblemType}
                        timeLimit={timeLimit}
                        setTimeLimit={setTimeLimit}
                        isGenerating={isGenerating}
                        onSubmit={handleSubmit}
                    />

                    {repoData && (
                        <div className="card" style={{ marginTop: '2rem' }}>
                            <h2 className="card-title">
                                <span className="emoji">📊</span>
                                Repository Data
                            </h2>
                            <div className="result-meta">
                                <div className="meta-item">
                                    <div className="meta-label">Name</div>
                                    <div className="meta-value">{repoData.name}</div>
                                </div>
                                <div className="meta-item">
                                    <div className="meta-label">Language</div>
                                    <div className="meta-value">{repoData.language}</div>
                                </div>
                                <div className="meta-item">
                                    <div className="meta-label">Files</div>
                                    <div className="meta-value">{repoData.files}</div>
                                </div>
                                <div className="meta-item">
                                    <div className="meta-label">Issues</div>
                                    <div className="meta-value">{repoData.issues}</div>
                                </div>
                                <div className="meta-item">
                                    <div className="meta-label">PRs</div>
                                    <div className="meta-value">{repoData.prs}</div>
                                </div>
                                <div className="meta-item">
                                    <div className="meta-label">Commits</div>
                                    <div className="meta-value">{repoData.commits}</div>
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                <div className="right-column">
                    <TechnicalViewSelector activeView={activeView} setActiveView={setActiveView} />
                    
                    {activeView === 'agents' && (
                        <>
                            <AgentDashboard
                                agents={AGENTS}
                                statuses={agentStatuses}
                                details={agentDetails}
                                isGenerating={isGenerating}
                            />
                            <div className="card" style={{ marginTop: '2rem' }}>
                                <h2 className="card-title">
                                    <span className="emoji">💻</span>
                                    Live Terminal View
                                </h2>
                                <ActivityLog logs={activityLog} logEndRef={logEndRef} />
                            </div>
                        </>
                    )}
                    
                    {activeView === 'architecture' && (
                        <ArchitectureView agents={AGENTS} statuses={agentStatuses} />
                    )}
                    
                    {activeView === 'a2a' && (
                        <A2AProtocolView messages={a2aMessages} />
                    )}
                    
                    {activeView === 'prompts' && (
                        <AgentPromptsView agents={AGENTS} />
                    )}
                </div>
            </div>

            {result && (
                <ResultsDisplay result={result} onDownload={downloadResult} />
            )}
        </div>
    );
}

function ConnectionStatus({ connected }) {
    return (
        <div className={`connection-status ${connected ? 'connected' : 'disconnected'}`}>
            <div className={`status-dot ${connected ? 'running' : 'error'}`}></div>
            {connected ? 'Connected' : 'Disconnected'}
        </div>
    );
}

function InputForm({
    repoUrl,
    setRepoUrl,
    difficulty,
    setDifficulty,
    problemType,
    setProblemType,
    timeLimit,
    setTimeLimit,
    isGenerating,
    onSubmit
}) {
    return (
        <div className="card">
            <h2 className="card-title">
                <span className="emoji">⚙️</span>
                Configuration
            </h2>
            <form className="input-form" onSubmit={onSubmit}>
                <div className="form-group">
                    <label className="form-label">GitHub Repository</label>
                    <input
                        type="text"
                        className="form-input"
                        placeholder="e.g., owner/repo or full URL"
                        value={repoUrl}
                        onChange={(e) => setRepoUrl(e.target.value)}
                        disabled={isGenerating}
                    />
                </div>

                <div className="form-group">
                    <label className="form-label">Difficulty Level</label>
                    <select
                        className="form-select"
                        value={difficulty}
                        onChange={(e) => setDifficulty(e.target.value)}
                        disabled={isGenerating}
                    >
                        <option value="easy">Easy</option>
                        <option value="medium">Medium</option>
                        <option value="hard">Hard</option>
                        <option value="expert">Expert</option>
                    </select>
                </div>

                <div className="form-group">
                    <label className="form-label">Problem Type</label>
                    <select
                        className="form-select"
                        value={problemType}
                        onChange={(e) => setProblemType(e.target.value)}
                        disabled={isGenerating}
                    >
                        <option value="feature">Feature Implementation</option>
                        <option value="bug-fix">Bug Fix</option>
                        <option value="refactor">Refactoring</option>
                        <option value="optimization">Optimization</option>
                    </select>
                </div>

                <div className="form-group">
                    <label className="form-label">Time Limit (minutes)</label>
                    <select
                        className="form-select"
                        value={timeLimit}
                        onChange={(e) => setTimeLimit(e.target.value)}
                        disabled={isGenerating}
                    >
                        <option value="60">60 minutes</option>
                        <option value="120">120 minutes</option>
                        <option value="180">180 minutes</option>
                        <option value="240">240 minutes</option>
                    </select>
                </div>

                <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={isGenerating || !repoUrl.trim()}
                >
                    {isGenerating ? '🔄 Generating...' : '🚀 Generate Assessment'}
                </button>
            </form>
        </div>
    );
}

function AgentDashboard({ agents, statuses, details, isGenerating }) {
    return (
        <div className="card">
            <h2 className="card-title">
                <span className="emoji">🤖</span>
                Multi-Agent System
            </h2>
            <div className="agent-grid">
                {agents.map(agent => (
                    <AgentCard
                        key={agent.id}
                        agent={agent}
                        status={statuses[agent.id]?.status || 'pending'}
                        message={statuses[agent.id]?.message || 'Waiting...'}
                        details={details[agent.id]}
                        isGenerating={isGenerating}
                    />
                ))}
            </div>
        </div>
    );
}

function AgentCard({ agent, status, message, details, isGenerating }) {
    const [expanded, setExpanded] = useState(false);
    const statusClass = isGenerating && status !== 'complete' ? status : 'pending';
    const hasDetails = details && (details.input || details.output);
    
    return (
        <div className={`agent-card ${statusClass}`}>
            <div className="agent-header">
                <div className="agent-icon">{agent.icon}</div>
                <div className="agent-info">
                    <div className="agent-name">{agent.name}</div>
                    <div className="agent-desc">{agent.description}</div>
                </div>
            </div>
            <div className="agent-status">
                <div className={`status-dot ${statusClass}`}></div>
                <span>{message}</span>
            </div>
            
            {hasDetails && (
                <div className="agent-details-toggle">
                    <button 
                        className="details-btn" 
                        onClick={() => setExpanded(!expanded)}
                    >
                        {expanded ? '▼ Hide Details' : '▶ Show Details'}
                    </button>
                </div>
            )}
            
            {expanded && hasDetails && (
                <div className="agent-details-content">
                    {details.input && (
                        <div className="detail-section">
                            <div className="detail-header">📥 INPUT</div>
                            <pre className="detail-data">{JSON.stringify(details.input, null, 2)}</pre>
                        </div>
                    )}
                    {details.output && (
                        <div className="detail-section">
                            <div className="detail-header">📤 OUTPUT</div>
                            <pre className="detail-data">{JSON.stringify(details.output, null, 2)}</pre>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

function ActivityLog({ logs, logEndRef }) {
    return (
        <div className="activity-log">
            {logs.length === 0 && (
                <div style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: '2rem' }}>
                    Terminal view will show live agent communications...
                </div>
            )}
            {logs.map((log, index) => {
                const isDetail = log.level === 'detail';
                const isError = log.level === 'error';
                const isComplete = log.level === 'complete';
                
                return (
                    <div key={index} className={`log-entry ${isDetail ? 'log-detail' : ''} ${isError ? 'log-error' : ''}`}>
                        <div className="log-meta">
                            <span className="log-timestamp">{log.timestamp}</span>
                            <span className={`log-agent agent-${log.agent.toLowerCase().replace(/\s+/g, '-')}`}>
                                [{log.agent}]
                            </span>
                        </div>
                        {isDetail ? (
                            <pre className="log-data">{log.message.replace(/^(INPUT|OUTPUT):\s*/, '')}</pre>
                        ) : (
                            <div className="log-message">
                                {isComplete && '✅ '}
                                {isError && '❌ '}
                                {log.message}
                            </div>
                        )}
                    </div>
                );
            })}
            <div ref={logEndRef} />
        </div>
    );
}

function ResultsDisplay({ result, onDownload }) {
    const assessment = result.assessment || {};
    const problem = assessment.problem || {};
    const validation = assessment.validation || {};
    const scores = validation.scores || {};

    return (
        <div className="results-container">
            <div className="card">
                <h2 className="card-title">
                    <span className="emoji">🎉</span>
                    Assessment Generated
                </h2>

                <div className="result-section">
                    <h3 className="result-title">{problem.title || 'N/A'}</h3>
                    
                    <div className="result-meta">
                        <div className="meta-item">
                            <div className="meta-label">Difficulty</div>
                            <div className="meta-value">{problem.difficulty || 'N/A'}</div>
                        </div>
                        <div className="meta-item">
                            <div className="meta-label">Time Limit</div>
                            <div className="meta-value">{problem.estimated_time || 'N/A'} min</div>
                        </div>
                        <div className="meta-item">
                            <div className="meta-label">Requirements</div>
                            <div className="meta-value">{problem.requirements?.length || 0}</div>
                        </div>
                        <div className="meta-item">
                            <div className="meta-label">Tech Stack</div>
                            <div className="meta-value">{problem.tech_stack?.join(', ') || 'N/A'}</div>
                        </div>
                    </div>

                    <div className="result-description">
                        <strong>Description:</strong>
                        <p>{problem.description || 'N/A'}</p>
                    </div>

                    {problem.requirements && problem.requirements.length > 0 && (
                        <>
                            <h4 style={{ marginTop: '1.5rem', marginBottom: '1rem' }}>Requirements</h4>
                            <ul className="requirements-list">
                                {problem.requirements.map((req, idx) => (
                                    <li key={idx}>{req}</li>
                                ))}
                            </ul>
                        </>
                    )}

                    {problem.acceptance_criteria && problem.acceptance_criteria.length > 0 && (
                        <>
                            <h4 style={{ marginTop: '1.5rem', marginBottom: '1rem' }}>Acceptance Criteria</h4>
                            <ul className="requirements-list">
                                {problem.acceptance_criteria.map((criteria, idx) => (
                                    <li key={idx}>{criteria}</li>
                                ))}
                            </ul>
                        </>
                    )}
                </div>

                <button className="btn btn-download" onClick={onDownload}>
                    📥 Download Assessment JSON
                </button>
            </div>
        </div>
    );
}

function TechnicalViewSelector({ activeView, setActiveView }) {
    const views = [
        { id: 'agents', label: 'Agent Dashboard', icon: '🤖' },
        { id: 'architecture', label: 'Architecture', icon: '🏗️' },
        { id: 'a2a', label: 'A2A Protocol', icon: '🔄' },
        { id: 'prompts', label: 'Agent Prompts', icon: '📝' }
    ];
    
    return (
        <div className="view-selector">
            {views.map(view => (
                <button
                    key={view.id}
                    className={`view-btn ${activeView === view.id ? 'active' : ''}`}
                    onClick={() => setActiveView(view.id)}
                >
                    <span className="view-icon">{view.icon}</span>
                    <span className="view-label">{view.label}</span>
                </button>
            ))}
        </div>
    );
}

function ArchitectureView({ agents, statuses }) {
    return (
        <div className="card">
            <h2 className="card-title">
                <span className="emoji">🏗️</span>
                Multi-Agent Architecture
            </h2>
            
            <div className="architecture-diagram">
                <div className="arch-section">
                    <div className="arch-title">Data Collection</div>
                    <div className="arch-agent scanner">
                        <div className="arch-agent-icon">🔍</div>
                        <div className="arch-agent-name">Scanner Agent</div>
                        <div className="arch-agent-tech">GitHub MCP</div>
                        <div className={`arch-status ${statuses.scanner?.status || 'pending'}`}>
                            {statuses.scanner?.status || 'pending'}
                        </div>
                    </div>
                </div>
                
                <div className="arch-arrow">↓</div>
                
                <div className="arch-section">
                    <div className="arch-title">3-Loop Analysis (Parallel)</div>
                    <div className="arch-agents-grid">
                        {['code_analyzer', 'pr_analyzer', 'issue_analyzer', 'dependency_analyzer'].map(agentId => {
                            const agent = agents.find(a => a.id === agentId);
                            return (
                                <div key={agentId} className="arch-agent analyzer">
                                    <div className="arch-agent-icon">{agent?.icon}</div>
                                    <div className="arch-agent-name">{agent?.name}</div>
                                    <div className="arch-agent-tech">Gemini 2.5</div>
                                    <div className={`arch-status ${statuses[agentId]?.status || 'pending'}`}>
                                        {statuses[agentId]?.status || 'pending'}
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                    <div className="arch-note">💬 Agents communicate via A2A Protocol</div>
                </div>
                
                <div className="arch-arrow">↓</div>
                
                <div className="arch-section">
                    <div className="arch-title">Problem Generation</div>
                    <div className="arch-agent creator">
                        <div className="arch-agent-icon">✨</div>
                        <div className="arch-agent-name">Problem Creator</div>
                        <div className="arch-agent-tech">Gemini 2.5 Pro</div>
                        <div className={`arch-status ${statuses.problem_creator?.status || 'pending'}`}>
                            {statuses.problem_creator?.status || 'pending'}
                        </div>
                    </div>
                </div>
                
                <div className="arch-arrow">↓</div>
                
                <div className="arch-section">
                    <div className="arch-title">Quality Assurance</div>
                    <div className="arch-agent validator">
                        <div className="arch-agent-icon">✅</div>
                        <div className="arch-agent-name">QA Validator</div>
                        <div className="arch-agent-tech">Gemini 2.5 Flash</div>
                        <div className={`arch-status ${statuses.qa_validator?.status || 'pending'}`}>
                            {statuses.qa_validator?.status || 'pending'}
                        </div>
                    </div>
                    <div className="arch-note">🔁 Improvement loop if score &lt; 85</div>
                </div>
            </div>
            
            <div className="tech-stack">
                <h3 className="tech-title">Technology Stack</h3>
                <div className="tech-items">
                    <div className="tech-item">
                        <div className="tech-label">Agent Framework</div>
                        <div className="tech-value">Google ADK</div>
                    </div>
                    <div className="tech-item">
                        <div className="tech-label">Protocol</div>
                        <div className="tech-value">A2A (Agent2Agent)</div>
                    </div>
                    <div className="tech-item">
                        <div className="tech-label">MCP Integration</div>
                        <div className="tech-value">GitHub MCP Server</div>
                    </div>
                    <div className="tech-item">
                        <div className="tech-label">LLM Models</div>
                        <div className="tech-value">Gemini 2.5 Pro & Flash</div>
                    </div>
                    <div className="tech-item">
                        <div className="tech-label">Platform</div>
                        <div className="tech-value">Google Cloud / Vertex AI</div>
                    </div>
                </div>
            </div>
        </div>
    );
}

function A2AProtocolView({ messages }) {
    return (
        <div className="card">
            <h2 className="card-title">
                <span className="emoji">🔄</span>
                A2A Protocol Messages
            </h2>
            
            <div className="a2a-info">
                <div className="info-card">
                    <div className="info-label">Protocol Version</div>
                    <div className="info-value">1.0</div>
                </div>
                <div className="info-card">
                    <div className="info-label">Messages Sent</div>
                    <div className="info-value">{messages.length}</div>
                </div>
                <div className="info-card">
                    <div className="info-label">Message Types</div>
                    <div className="info-value">Request, Response, Broadcast</div>
                </div>
            </div>
            
            <div className="a2a-explanation">
                <h3>What is A2A?</h3>
                <p>Agent-to-Agent (A2A) Protocol is Google's standard for agent interoperability. It enables:</p>
                <ul>
                    <li><strong>Discovery</strong>: Agents can discover each other's capabilities</li>
                    <li><strong>Communication</strong>: Structured message passing between agents</li>
                    <li><strong>Collaboration</strong>: Multi-agent workflows and consensus building</li>
                </ul>
            </div>
            
            <div className="a2a-messages">
                <h3 className="messages-title">Live Message Flow</h3>
                {messages.length === 0 ? (
                    <div className="no-messages">No A2A messages yet. Start generation to see agent communication...</div>
                ) : (
                    <div className="messages-list">
                        {messages.map((msg, idx) => (
                            <div key={idx} className="a2a-message">
                                <div className="message-header">
                                    <span className="message-from">{msg.from}</span>
                                    <span className="message-arrow">→</span>
                                    <span className="message-to">{msg.to}</span>
                                    <span className="message-time">{new Date(msg.timestamp).toLocaleTimeString()}</span>
                                </div>
                                <div className="message-type">{msg.type.toUpperCase()}</div>
                                <pre className="message-data">{JSON.stringify(msg.data, null, 2)}</pre>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}

function AgentPromptsView({ agents }) {
    const agentPrompts = {
        scanner: {
            systemInstruction: "You are a GitHub repository scanner. Retrieve comprehensive data about repositories including metadata, file structure, issues, PRs, commits, README, and dependencies. Use GitHub MCP tools efficiently.",
            model: "gemini-2.5-flash",
            tools: ["GitHub MCP Server"],
            temperature: 0.1
        },
        code_analyzer: {
            systemInstruction: "Analyze codebase architecture, patterns, and complexity. Focus on: architectural patterns (MVC, microservices, etc.), code quality metrics, technical debt, and feature opportunities. Provide structured analysis.",
            model: "gemini-2.5-pro",
            tools: [],
            temperature: 0.3
        },
        pr_analyzer: {
            systemInstruction: "Analyze pull request patterns to extract development insights. Identify common change types, frequent files, workflow patterns, recent features, and common bugs. Suggest problem opportunities based on PR trends.",
            model: "gemini-2.5-flash",
            tools: [],
            temperature: 0.4
        },
        issue_analyzer: {
            systemInstruction: "Analyze GitHub issues to extract problem patterns and feature requests. Categorize issues (bugs, features, enhancements), identify priority issues, and suggest coding problems based on user pain points.",
            model: "gemini-2.5-flash",
            tools: [],
            temperature: 0.4
        },
        dependency_analyzer: {
            systemInstruction: "Analyze repository dependencies and tech stack. Identify frameworks, libraries, runtime environment, dependency health (outdated, vulnerable), and integration opportunities.",
            model: "gemini-2.5-flash",
            tools: [],
            temperature: 0.3
        },
        problem_creator: {
            systemInstruction: "Create realistic, implementable coding problems based on repository analysis. Ensure problems are: aligned with repo tech stack, completable in time limit, self-contained (no private repo access needed), and have clear testable requirements.",
            model: "gemini-2.5-pro",
            tools: [],
            temperature: 0.7
        },
        qa_validator: {
            systemInstruction: "Validate coding problem quality across 4 dimensions: Feasibility (completable in time, context provided), Quality (clear description, testable requirements), Technical (correct tech stack, proper patterns), Educational (relevant skills, appropriate difficulty). Score each 0-100, require 85+ overall.",
            model: "gemini-2.5-flash",
            tools: [],
            temperature: 0.3
        }
    };
    
    return (
        <div className="card">
            <h2 className="card-title">
                <span className="emoji">📝</span>
                Agent System Instructions
            </h2>
            
            <div className="prompts-explanation">
                <p>Each agent has specialized system instructions that define its role and behavior. These prompts are carefully engineered to ensure high-quality, collaborative analysis.</p>
            </div>
            
            <div className="prompts-list">
                {agents.map(agent => {
                    const prompt = agentPrompts[agent.id];
                    if (!prompt) return null;
                    
                    return (
                        <div key={agent.id} className="prompt-card">
                            <div className="prompt-header">
                                <span className="prompt-icon">{agent.icon}</span>
                                <div className="prompt-info">
                                    <h3 className="prompt-name">{agent.name}</h3>
                                    <div className="prompt-meta">
                                        <span className="prompt-model">{prompt.model}</span>
                                        <span className="prompt-temp">temp: {prompt.temperature}</span>
                                    </div>
                                </div>
                            </div>
                            
                            {prompt.tools.length > 0 && (
                                <div className="prompt-tools">
                                    <strong>Tools:</strong> {prompt.tools.join(', ')}
                                </div>
                            )}
                            
                            <div className="prompt-instruction">
                                <strong>System Instruction:</strong>
                                <p>{prompt.systemInstruction}</p>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}

// Render the app
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
