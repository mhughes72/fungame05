import { useState } from 'react'
import { startGame } from '../api.js'
import LoadingOverlay from './LoadingOverlay.jsx'
import NavButtons from './NavButtons.jsx'

function ModeCard({ selected, onClick, title, tag, description }) {
  return (
    <button
      onClick={onClick}
      className={`text-left p-6 border-2 transition-all w-full ${
        selected
          ? 'border-amber-500 bg-slate-900'
          : 'border-slate-700 bg-slate-900 hover:border-slate-500'
      }`}
    >
      <div className={`text-xl font-bold mb-1 ${selected ? 'text-amber-400' : 'text-slate-200'}`}>
        {title}
      </div>
      <div className="text-xs text-slate-500 uppercase tracking-widest mb-3">{tag}</div>
      <p className="text-slate-400 text-sm leading-relaxed">{description}</p>
      {selected && (
        <div className="mt-3 text-amber-500 text-xs font-bold tracking-widest">✓ SELECTED</div>
      )}
    </button>
  )
}

export default function HomeScreen({ onStart }) {
  const [mode, setMode] = useState('classic')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function handleStart() {
    setLoading(true)
    setError(null)
    try {
      const data = await startGame(mode)
      onStart(data)
    } catch (e) {
      setError(e.message || 'Failed to start game. Is the server running?')
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center p-6 relative">
      {loading && <LoadingOverlay message="INITIALISING..." />}

      {/* Nav buttons — top right */}
      <div className="absolute top-4 right-6">
        <NavButtons />
      </div>

      {/* Emblem / title */}
      <div className="text-center mb-12">
        <div className="text-red-600 text-5xl font-black tracking-widest mb-3">■</div>
        <h1 className="text-4xl font-bold text-slate-100 tracking-wide mb-2">
          REPUBLIC OF VERIDIA
        </h1>
        <p className="text-amber-400 text-sm uppercase tracking-widest mb-4">
          Political Simulator
        </p>
        <p className="text-slate-500 text-sm italic max-w-sm mx-auto leading-relaxed">
          You have been elected leader of a small, troubled republic.
          Survive twelve months. Make decisions. Live with them.
        </p>
      </div>

      {/* Mode selection */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl w-full mb-8">
        <ModeCard
          selected={mode === 'classic'}
          onClick={() => setMode('classic')}
          title="Classic"
          tag="Authored Crises"
          description="Face curated political crises with multiple-choice responses. Each option has authored consequences. Good for a structured, balanced experience."
        />
        <ModeCard
          selected={mode === 'freeform'}
          onClick={() => setMode('freeform')}
          title="Freeform"
          tag="AI-Generated"
          description="The AI generates crises from your decision history. Respond in your own words. Anything is a valid action — the AI decides the consequences."
        />
      </div>

      {/* Error */}
      {error && (
        <div className="mb-4 text-red-400 text-sm border border-red-900 bg-red-950/50 px-4 py-2 max-w-sm text-center">
          {error}
        </div>
      )}

      {/* Start button */}
      <button
        onClick={handleStart}
        disabled={loading}
        className="bg-red-700 hover:bg-red-600 disabled:bg-slate-800 disabled:text-slate-600 text-white font-bold py-3 px-12 text-lg tracking-widest transition-colors"
      >
        BEGIN TENURE
      </button>

      <p className="text-slate-700 text-xs mt-6 italic">
        The country will not be improved by optimism.
      </p>
    </div>
  )
}
