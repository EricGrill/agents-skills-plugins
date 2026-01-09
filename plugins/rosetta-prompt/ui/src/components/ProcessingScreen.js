import { motion, AnimatePresence } from 'framer-motion'
import { useStore } from '../store'
import { useEffect, useRef } from 'react'

const LOG_COLORS = {
  system: '#8a8a8a',
  agent: '#1a1a1a',
  thinking: '#8a8a8a',
  spawn: '#2d4a3e',
  tool: '#c84b31',
  success: '#2d4a3e',
  result: '#1a1a1a',
  error: '#c84b31'
}

export function ProcessingScreen() {
  const { logs, currentStep, progress } = useStore()
  const logsEndRef = useRef(null)
  
  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [logs])
  
  return (
    <motion.div 
      className="processing-screen"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="processing-container">
        <motion.div 
          className="processing-header"
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.1 }}
        >
          <div className="processing-icon">
            <motion.div 
              className="spinner"
              animate={{ rotate: 360 }}
              transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
            >
              ◎
            </motion.div>
          </div>
          <h2 className="processing-title">Processing</h2>
          <p className="processing-step">{currentStep || 'Initializing'}</p>
        </motion.div>
        
        <motion.div 
          className="progress-section"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          <div className="progress-bar">
            <motion.div 
              className="progress-fill"
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.3 }}
            />
          </div>
          <span className="progress-text">{progress}%</span>
        </motion.div>
        
        <motion.div 
          className="logs-container"
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          <div className="logs-header">
            <span className="logs-title">Log</span>
            <span className="logs-count">{logs.length}</span>
          </div>
          <div className="logs-window">
            <AnimatePresence mode="popLayout">
              {logs.map((log) => (
                <motion.div
                  key={log.id}
                  className="log-entry"
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.15 }}
                >
                  <span className="log-time">
                    {log.timestamp.toLocaleTimeString('en-US', { 
                      hour12: false, 
                      hour: '2-digit', 
                      minute: '2-digit', 
                      second: '2-digit'
                    })}
                  </span>
                  <span className="log-prefix" style={{ color: LOG_COLORS[log.type] || LOG_COLORS.system }}>
                    {log.type.toUpperCase()}
                  </span>
                  <span className="log-message">{log.message}</span>
                </motion.div>
              ))}
            </AnimatePresence>
            <div ref={logsEndRef} />
          </div>
        </motion.div>
      </div>
    </motion.div>
  )
}
