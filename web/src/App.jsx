import { useState } from 'react'
import HomeScreen from './components/HomeScreen.jsx'
import GameScreen from './components/GameScreen.jsx'
import ConsequencesPanel from './components/ConsequencesPanel.jsx'
import EndScreen from './components/EndScreen.jsx'

/**
 * View flow:
 *   home  →  playing  →  consequences  →  (playing | ended)
 *                                        ↑ based on game_status
 */
export default function App() {
  const [view, setView] = useState('home')
  const [gameData, setGameData] = useState(null)

  function handleStart(data) {
    setGameData(data)
    setView('playing')
  }

  function handleResolve(data) {
    setGameData(data)
    setView('consequences')
  }

  function handleContinue() {
    if (!gameData || gameData.game_status !== 'active') {
      setView('ended')
    } else {
      setView('playing')
    }
  }

  function handleRestart() {
    setGameData(null)
    setView('home')
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      {view === 'home' && (
        <HomeScreen onStart={handleStart} />
      )}
      {view === 'playing' && gameData && (
        <GameScreen gameData={gameData} onResolve={handleResolve} />
      )}
      {view === 'consequences' && gameData && (
        <ConsequencesPanel gameData={gameData} onContinue={handleContinue} />
      )}
      {view === 'ended' && gameData && (
        <EndScreen gameData={gameData} onRestart={handleRestart} />
      )}
    </div>
  )
}
