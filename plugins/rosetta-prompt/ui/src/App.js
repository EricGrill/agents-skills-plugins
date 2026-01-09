import { AnimatePresence } from 'framer-motion'
import { useStore } from './store'
import { InputScreen } from './components/InputScreen'
import { ProcessingScreen } from './components/ProcessingScreen'
import { ResultsScreen } from './components/ResultsScreen'
import './util'

export function App() {
  const screen = useStore((state) => state.screen)
  
  return (
    <div className="app">
      <AnimatePresence mode="wait">
        {screen === 'input' && <InputScreen key="input" />}
        {screen === 'processing' && <ProcessingScreen key="processing" />}
        {screen === 'results' && <ResultsScreen key="results" />}
      </AnimatePresence>
    </div>
  )
}
