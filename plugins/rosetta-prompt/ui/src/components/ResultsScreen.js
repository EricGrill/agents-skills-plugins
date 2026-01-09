import * as THREE from 'three'
import { useRef, useState, useEffect } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { Text, RoundedBox, PerspectiveCamera, ScrollControls, useScroll } from '@react-three/drei'
import { easing } from 'maath'
import { motion, AnimatePresence } from 'framer-motion'
import { useStore } from '../store'

const PROVIDER_CONFIG = {
  openai: { color: '#10a37f', gradient: ['#10a37f', '#0d8f6f'] },
  anthropic: { color: '#d4a574', gradient: ['#d4a574', '#c49464'] },
  google: { color: '#4285f4', gradient: ['#4285f4', '#3275e4'] },
  kimi: { color: '#ff6b6b', gradient: ['#ff6b6b', '#ef5b5b'] },
  mistral: { color: '#ff7000', gradient: ['#ff7000', '#ef6000'] },
  deepseek: { color: '#00d4aa', gradient: ['#00d4aa', '#00c49a'] },
  meta: { color: '#0084ff', gradient: ['#0084ff', '#0074ef'] },
  default: { color: '#888888', gradient: ['#888888', '#787878'] }
}

export function ResultsScreen() {
  const { results, showPopup, selectedCard, closePopup, reset, logs } = useStore()
  const [expandedLog, setExpandedLog] = useState(null)
  const [showLogs, setShowLogs] = useState(true)
  
  if (!results) return null
  
  const providers = Object.keys(results.optimized)
  const totalChanges = Object.values(results.optimized).reduce((acc, r) => acc + (r.changes?.length || 0), 0)
  
  return (
    <motion.div 
      className="results-screen"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      {/* 3D Ring Carousel with Scroll Controls */}
      <div className="arcade-container">
        <Canvas shadows>
          <PerspectiveCamera makeDefault position={[0, 1.5, 10]} fov={40} />
          <color attach="background" args={['#080808']} />
          <fog attach="fog" args={['#080808', 10, 25]} />
          
          {/* Dramatic lighting */}
          <ambientLight intensity={0.3} />
          <spotLight 
            position={[0, 15, 0]} 
            angle={0.4} 
            penumbra={1} 
            intensity={1.5} 
            castShadow
            shadow-mapSize={[1024, 1024]}
          />
          <pointLight position={[-8, 5, -8]} intensity={0.4} color="#c84b31" />
          <pointLight position={[8, 5, -8]} intensity={0.4} color="#4285f4" />
          
          {/* Ground with reflection */}
          <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -2.5, 0]} receiveShadow>
            <planeGeometry args={[100, 100]} />
            <meshStandardMaterial 
              color="#0a0a0a" 
              metalness={0.95} 
              roughness={0.2}
            />
          </mesh>
          
          {/* Scroll-controlled ring */}
          <ScrollControls pages={4} infinite>
            <ScrollRing providers={providers} results={results.optimized} />
          </ScrollControls>
        </Canvas>
      </div>
      
      {/* Header */}
      <div className="results-overlay">
        <motion.div 
          className="arcade-header"
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          <h2>OPTIMIZATION COMPLETE</h2>
          <p>Scroll to rotate · Click any card for details</p>
        </motion.div>
        
        <motion.button
          className="back-btn"
          onClick={reset}
          initial={{ x: -20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ delay: 0.4 }}
        >
          ← New Prompt
        </motion.button>
        
        {/* Enhanced Logs Panel */}
        <motion.div 
          className="results-logs-panel"
          initial={{ x: 20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          <div className="logs-panel-header" onClick={() => setShowLogs(!showLogs)}>
            <span>Agent Execution Log</span>
            <span className="logs-toggle">{showLogs ? '−' : '+'}</span>
          </div>
          {showLogs && (
            <div className="logs-panel-content">
              {logs.map((log, idx) => (
                <div 
                  key={log.id} 
                  className={`log-item ${expandedLog === idx ? 'expanded' : ''}`}
                  onClick={() => setExpandedLog(expandedLog === idx ? null : idx)}
                >
                  <div className="log-main">
                    <span className="log-step">{String(idx + 1).padStart(2, '0')}</span>
                    <span className="log-type" data-type={log.type}>{log.type}</span>
                    <span className="log-msg">{log.message}</span>
                  </div>
                  {expandedLog === idx && (
                    <div className="log-details">
                      <div className="log-detail-row">
                        <span className="detail-label">Timestamp:</span>
                        <span>{log.timestamp.toLocaleTimeString()}</span>
                      </div>
                      <div className="log-detail-row">
                        <span className="detail-label">Type:</span>
                        <span>{log.type.toUpperCase()}</span>
                      </div>
                      {log.provider && (
                        <div className="log-detail-row">
                          <span className="detail-label">Provider:</span>
                          <span>{log.provider.toUpperCase()}</span>
                        </div>
                      )}
                      <div className="log-detail-row">
                        <span className="detail-label">Action:</span>
                        <span>{getLogDescription(log)}</span>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </motion.div>
        
        {/* Stats Bar */}
        <motion.div 
          className="arcade-stats"
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.4 }}
        >
          <div className="stat-pill">
            <span className="stat-num">{providers.length}</span>
            <span className="stat-txt">PROVIDERS</span>
          </div>
          <div className="stat-pill">
            <span className="stat-num">{totalChanges}</span>
            <span className="stat-txt">CHANGES</span>
          </div>
          <div className="stat-pill">
            <span className="stat-num">{results.original.length}</span>
            <span className="stat-txt">INPUT</span>
          </div>
        </motion.div>
      </div>
      
      <AnimatePresence>
        {showPopup && selectedCard && (
          <PromptPopup 
            provider={selectedCard}
            result={results.optimized[selectedCard]}
            original={results.original}
            onClose={closePopup}
          />
        )}
      </AnimatePresence>
    </motion.div>
  )
}

function getLogDescription(log) {
  const descriptions = {
    system: 'System initialization or status update',
    agent: 'Main orchestrator agent action',
    thinking: 'Agent reasoning and planning step',
    spawn: 'Spawning parallel worker agent',
    tool: 'Executing tool to read provider documentation',
    success: 'Task completed successfully',
    result: 'Provider optimization result',
    error: 'Error occurred during processing'
  }
  return descriptions[log.type] || 'Agent action'
}

function ScrollRing({ providers, results }) {
  const groupRef = useRef()
  const scroll = useScroll()
  const radius = 4
  const count = providers.length
  
  useFrame((state, delta) => {
    // Rotate based on scroll position
    const targetRotation = -scroll.offset * Math.PI * 2
    groupRef.current.rotation.y = targetRotation
    
    // Gentle floating
    groupRef.current.position.y = Math.sin(state.clock.elapsedTime * 0.4) * 0.1
  })
  
  return (
    <group ref={groupRef} position={[0, 0, 0]}>
      {/* Ring base glow */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -2, 0]}>
        <ringGeometry args={[radius - 0.8, radius + 0.8, 64]} />
        <meshBasicMaterial color="#c84b31" transparent opacity={0.08} />
      </mesh>
      
      {/* Center point light */}
      <pointLight position={[0, 0, 0]} intensity={0.3} color="#c84b31" distance={5} />
      
      {providers.map((provider, i) => {
        const angle = (i / count) * Math.PI * 2
        const x = Math.sin(angle) * radius
        const z = Math.cos(angle) * radius
        
        return (
          <DoubleSidedCard
            key={provider}
            provider={provider}
            result={results[provider]}
            position={[x, 0, z]}
            rotation={[0, -angle + Math.PI, 0]}
            index={i}
          />
        )
      })}
    </group>
  )
}

function DoubleSidedCard({ provider, result, position, rotation, index }) {
  const meshRef = useRef()
  const [hovered, setHovered] = useState(false)
  const selectCard = useStore((state) => state.selectCard)
  const config = PROVIDER_CONFIG[provider] || PROVIDER_CONFIG.default
  const changesCount = result?.changes?.length || 0
  const success = result?.success
  const providerName = provider.charAt(0).toUpperCase() + provider.slice(1)
  
  useFrame((state, delta) => {
    // Hover lift
    const targetY = hovered ? position[1] + 0.3 : position[1]
    easing.damp(meshRef.current.position, 'y', targetY, 0.2, delta)
    
    // Hover scale
    const targetScale = hovered ? 1.08 : 1
    easing.damp3(meshRef.current.scale, [targetScale, targetScale, targetScale], 0.15, delta)
  })
  
  const handleClick = (e) => {
    e.stopPropagation()
    selectCard(provider)
  }

  return (
    <group 
      ref={meshRef}
      position={position}
      rotation={rotation}
      onPointerOver={(e) => { e.stopPropagation(); setHovered(true); document.body.style.cursor = 'pointer' }}
      onPointerOut={() => { setHovered(false); document.body.style.cursor = 'auto' }}
      onClick={handleClick}
    >
      {/* Card shadow */}
      <mesh position={[0, -1.8, 0.2]} rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[1.6, 0.1]} />
        <meshBasicMaterial color="#000" transparent opacity={0.4} />
      </mesh>
      
      {/* Main card body - white front */}
      <RoundedBox args={[1.5, 2.2, 0.1]} radius={0.1} smoothness={4} castShadow>
        <meshStandardMaterial 
          color="#fefefe" 
          metalness={0.05} 
          roughness={0.4}
        />
      </RoundedBox>
      
      {/* ========== FRONT SIDE ========== */}
      <group position={[0, 0, 0.06]}>
        {/* Color accent header */}
        <mesh position={[0, 0.9, 0]}>
          <boxGeometry args={[1.3, 0.25, 0.02]} />
          <meshStandardMaterial color={config.color} metalness={0.2} roughness={0.6} />
        </mesh>
        
        {/* Provider name */}
        <Text
          position={[0, 0.58, 0]}
          fontSize={0.14}
          color={config.color}
          anchorX="center"
          anchorY="middle"
          letterSpacing={0.08}
        >
          {providerName.toUpperCase()}
        </Text>
        
        {/* Big number - changes count */}
        <Text
          position={[0, 0, 0]}
          fontSize={0.7}
          color="#1a1a1a"
          anchorX="center"
          anchorY="middle"
        >
          {changesCount}
        </Text>
        
        {/* Changes label */}
        <Text
          position={[0, -0.45, 0]}
          fontSize={0.09}
          color="#666666"
          anchorX="center"
          anchorY="middle"
          letterSpacing={0.18}
        >
          CHANGES
        </Text>
        
        {/* Divider line */}
        <mesh position={[0, -0.62, 0]}>
          <boxGeometry args={[1, 0.005, 0.01]} />
          <meshBasicMaterial color="#e0e0e0" />
        </mesh>
        
        {/* Status */}
        <Text
          position={[0, -0.78, 0]}
          fontSize={0.07}
          color={success ? '#22863a' : '#cb2431'}
          anchorX="center"
          anchorY="middle"
        >
          {success ? '● OPTIMIZED' : '○ ERROR'}
        </Text>
        
        {/* Hint */}
        <Text
          position={[0, -0.95, 0]}
          fontSize={0.045}
          color="#aaaaaa"
          anchorX="center"
          anchorY="middle"
        >
          CLICK TO VIEW
        </Text>
      </group>
      
      {/* ========== BACK SIDE (rotated 180 degrees) ========== */}
      <group position={[0, 0, -0.06]} rotation={[0, Math.PI, 0]}>
        {/* Color accent header */}
        <mesh position={[0, 0.9, 0]}>
          <boxGeometry args={[1.3, 0.25, 0.02]} />
          <meshStandardMaterial color={config.color} metalness={0.2} roughness={0.6} />
        </mesh>
        
        {/* Provider name */}
        <Text
          position={[0, 0.58, 0]}
          fontSize={0.14}
          color={config.color}
          anchorX="center"
          anchorY="middle"
          letterSpacing={0.08}
        >
          {providerName.toUpperCase()}
        </Text>
        
        {/* Big number - changes count */}
        <Text
          position={[0, 0, 0]}
          fontSize={0.7}
          color="#1a1a1a"
          anchorX="center"
          anchorY="middle"
        >
          {changesCount}
        </Text>
        
        {/* Changes label */}
        <Text
          position={[0, -0.45, 0]}
          fontSize={0.09}
          color="#666666"
          anchorX="center"
          anchorY="middle"
          letterSpacing={0.18}
        >
          CHANGES
        </Text>
        
        {/* Divider line */}
        <mesh position={[0, -0.62, 0]}>
          <boxGeometry args={[1, 0.005, 0.01]} />
          <meshBasicMaterial color="#e0e0e0" />
        </mesh>
        
        {/* Status */}
        <Text
          position={[0, -0.78, 0]}
          fontSize={0.07}
          color={success ? '#22863a' : '#cb2431'}
          anchorX="center"
          anchorY="middle"
        >
          {success ? '● OPTIMIZED' : '○ ERROR'}
        </Text>
        
        {/* Hint */}
        <Text
          position={[0, -0.95, 0]}
          fontSize={0.045}
          color="#aaaaaa"
          anchorX="center"
          anchorY="middle"
        >
          CLICK TO VIEW
        </Text>
      </group>
      
      {/* Hover glow effect */}
      {hovered && (
        <>
          <pointLight position={[0, 0, 1]} intensity={0.5} color={config.color} distance={3} />
          <mesh position={[0, 0, 0]}>
            <boxGeometry args={[1.6, 2.3, 0.15]} />
            <meshBasicMaterial color={config.color} transparent opacity={0.1} />
          </mesh>
        </>
      )}
    </group>
  )
}

function PromptPopup({ provider, result, original, onClose }) {
  const providerName = provider.charAt(0).toUpperCase() + provider.slice(1)
  const config = PROVIDER_CONFIG[provider] || PROVIDER_CONFIG.default
  
  return (
    <motion.div
      className="popup-overlay"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={onClose}
    >
      <motion.div
        className="popup-content"
        initial={{ scale: 0.9, opacity: 0, y: 20 }}
        animate={{ scale: 1, opacity: 1, y: 0 }}
        exit={{ scale: 0.9, opacity: 0, y: 20 }}
        onClick={(e) => e.stopPropagation()}
        style={{ '--accent-color': config.color }}
      >
        <div className="popup-header" style={{ borderBottomColor: config.color }}>
          <div className="popup-provider">
            <span className="popup-name">{providerName}</span>
            {result?.success && <span className="popup-badge" style={{ background: config.color }}>{result.changes?.length} changes</span>}
          </div>
          <button className="popup-close" onClick={onClose}>×</button>
        </div>
        
        <div className="popup-body">
          {result?.success ? (
            <>
              <div className="prompt-section">
                <h3>Optimized Prompt</h3>
                <pre className="prompt-text optimized" style={{ borderLeftColor: config.color }}>{result.prompt}</pre>
              </div>
              
              {result.changes && result.changes.length > 0 && (
                <div className="changes-section">
                  <h3>Changes Applied ({result.changes.length})</h3>
                  <div className="changes-list">
                    {result.changes.map((change, i) => (
                      <div key={i} className="change-item" style={{ borderLeftColor: config.color }}>
                        <span className="change-category" style={{ background: config.color }}>{change.category}</span>
                        <p className="change-description">{change.description}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              <div className="prompt-section original">
                <h3>Original ({original.length} chars)</h3>
                <pre className="prompt-text">{original}</pre>
              </div>
            </>
          ) : (
            <div className="error-section">
              <span className="error-icon">×</span>
              <p>{result?.error || 'Optimization failed'}</p>
            </div>
          )}
        </div>
        
        <div className="popup-footer">
          <button className="copy-btn" style={{ background: config.color }} onClick={() => {
            navigator.clipboard.writeText(result?.prompt || '')
          }}>
            Copy Optimized Prompt
          </button>
        </div>
      </motion.div>
    </motion.div>
  )
}
