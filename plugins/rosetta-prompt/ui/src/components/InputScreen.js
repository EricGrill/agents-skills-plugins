import { useEffect } from 'react'
import { motion } from 'framer-motion'
import { useStore } from '../store'

export function InputScreen() {
  const { 
    prompt, 
    setPrompt, 
    selectedProviders, 
    toggleProvider, 
    availableProviders,
    providersLoaded,
    fetchProviders,
    optimizePrompt 
  } = useStore()
  
  // Fetch providers on mount
  useEffect(() => {
    if (!providersLoaded) {
      fetchProviders()
    }
  }, [providersLoaded, fetchProviders])
  
  const canSubmit = prompt.trim().length > 0 && selectedProviders.length > 0
  
  return (
    <motion.div 
      className="input-screen"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.4 }}
    >
      <div className="input-container">
        <motion.div 
          className="logo-section"
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.1, duration: 0.5 }}
        >
          <div className="logo-icon">R—</div>
          <h1 className="logo-text">Rosetta Prompt</h1>
          <p className="tagline">Universal prompt optimization for every AI provider</p>
        </motion.div>
        
        <motion.div 
          className="prompt-section"
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.2, duration: 0.5 }}
        >
          <label className="input-label">Prompt</label>
          <textarea
            className="prompt-input"
            placeholder="Enter your prompt here..."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            rows={5}
          />
          <div className="char-count">{prompt.length}</div>
        </motion.div>
        
        <motion.div 
          className="providers-section"
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.3, duration: 0.5 }}
        >
          <label className="input-label">
            Target Providers 
            {availableProviders.length > 0 && (
              <span className="provider-count">({availableProviders.length} available)</span>
            )}
          </label>
          <div className="providers-grid" style={{ 
            gridTemplateColumns: `repeat(${Math.min(availableProviders.length, 4)}, 1fr)` 
          }}>
            {availableProviders.map((provider) => {
              const isSelected = selectedProviders.includes(provider)
              const displayName = provider.charAt(0).toUpperCase() + provider.slice(1)
              return (
                <motion.button
                  key={provider}
                  className={`provider-btn ${isSelected ? 'selected' : ''}`}
                  onClick={() => toggleProvider(provider)}
                  whileTap={{ scale: 0.98 }}
                >
                  <span className="provider-name">{displayName}</span>
                  {isSelected && <span className="check-mark">✓</span>}
                </motion.button>
              )
            })}
          </div>
          {!providersLoaded && (
            <div className="loading-providers">Loading providers...</div>
          )}
        </motion.div>
        
        <motion.div 
          className="submit-section"
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.4, duration: 0.5 }}
        >
          <motion.button
            className={`submit-btn ${canSubmit ? '' : 'disabled'}`}
            onClick={canSubmit ? optimizePrompt : undefined}
            whileHover={canSubmit ? { scale: 1.01 } : {}}
            whileTap={canSubmit ? { scale: 0.99 } : {}}
          >
            Optimize for {selectedProviders.length} provider{selectedProviders.length !== 1 ? 's' : ''}
          </motion.button>
        </motion.div>
        
        <motion.div 
          className="footer-info"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6, duration: 0.5 }}
        >
          <span>Agentic AI</span>
          <span className="separator">·</span>
          <span>Parallel processing</span>
          <span className="separator">·</span>
          <span>Auto-detected providers</span>
        </motion.div>
      </div>
    </motion.div>
  )
}
