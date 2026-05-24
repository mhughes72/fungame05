import { useState } from 'react'
import { resolveGame } from '../api.js'
import LoadingOverlay from './LoadingOverlay.jsx'
import StatGrid from './StatGrid.jsx'
import NavButtons from './NavButtons.jsx'

export default function GameScreen({ gameData, onResolve }) {
  const [choice, setChoice] = useState(null)
  const [inputText, setInputText] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const isClassic = gameData.mode === 'classic'
  const crisis = gameData.active_crisis

  const canSubmit = isClassic ? choice !== null : inputText.trim().length > 0

  async function handleSubmit() {
    if (!canSubmit || loading) return
    setLoading(true)
    setError(null)
    try {
      const payload = isClassic
        ? { choice_index: choice }
        : { player_input: inputText.trim() }
      const data = await resolveGame(gameData.game_id, payload)
      onResolve(data)
    } catch (e) {
      setError(e.message || 'Something went wrong. Try again.')
      setLoading(false)
    }
  }

  function handleKeyDown(e) {
    if (!isClassic && e.key === 'Enter' && e.ctrlKey) {
      handleSubmit()
    }
  }

  return (
    <div className="min-h-screen bg-slate-950">
      {loading && <LoadingOverlay message="PROCESSING DECISION..." />}

      {/* Top bar */}
      <div className="bg-slate-900 border-b border-slate-800 px-4 py-3 flex items-center justify-between sticky top-0 z-10">
        <div className="text-red-600 font-black tracking-widest text-sm">■ VERIDIA</div>
        <div className="flex items-center gap-5">
          <span className="text-slate-400 text-sm">
            MONTH <span className="text-slate-200 font-bold">{gameData.current_turn}</span>
            <span className="text-slate-600"> / {gameData.max_turns}</span>
          </span>
          <span className="text-xs text-slate-600 uppercase tracking-widest hidden sm:block">
            {gameData.mode}
          </span>
          <NavButtons />
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-4 lg:p-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

          {/* Left column: live stats */}
          <aside className="lg:col-span-1 space-y-4">
            <StatGrid
              national={gameData.national_stats}
              economy={gameData.economy_stats}
              factions={gameData.faction_support}
            />

            {/* Economy / faction pressure notes */}
            {((gameData.economy_drift_descriptions?.length ?? 0) > 0 ||
              (gameData.faction_pressure_descriptions?.length ?? 0) > 0) && (
              <div className="bg-slate-900 border border-slate-800 p-4">
                <div className="text-xs text-slate-500 uppercase tracking-widest mb-3 font-bold">
                  Background Conditions
                </div>
                {[
                  ...(gameData.economy_drift_descriptions ?? []),
                  ...(gameData.faction_pressure_descriptions ?? []),
                ].map((d, i) => (
                  <p key={i} className="text-slate-400 text-xs mb-1.5">• {d}</p>
                ))}
              </div>
            )}
          </aside>

          {/* Right column: crisis + decision */}
          <main className="lg:col-span-2 space-y-4">
            {/* Situation briefing (classic only) */}
            {gameData.situation_briefing && (
              <div className="bg-slate-900 border border-slate-700 p-5">
                <div className="text-xs text-slate-500 uppercase tracking-widest mb-2 font-bold">
                  Situation Report
                </div>
                <p className="text-slate-300 italic leading-relaxed text-sm">
                  {gameData.situation_briefing}
                </p>
              </div>
            )}

            {/* Crisis card */}
            <div className="bg-slate-900 border-l-4 border-amber-500 p-6">
              <div className="text-amber-400 text-xs uppercase tracking-widest mb-3 font-bold">
                Active Crisis
              </div>
              <h2 className="text-2xl font-bold text-slate-100 mb-4 leading-snug">
                {crisis?.title}
              </h2>
              <p className="text-slate-300 leading-relaxed">
                {crisis?.description}
              </p>
            </div>

            {/* Decision panel */}
            <div className="bg-slate-900 border border-slate-800 p-6">
              <div className="text-xs text-slate-500 uppercase tracking-widest mb-5 font-bold">
                {isClassic ? 'Select your response' : 'Your response (free text)'}
              </div>

              {isClassic ? (
                /* Classic: numbered option buttons */
                <div className="space-y-3">
                  {(crisis?.options ?? []).map((opt, i) => (
                    <button
                      key={i}
                      onClick={() => setChoice(i)}
                      className={`w-full text-left p-4 border-2 transition-all ${
                        choice === i
                          ? 'border-amber-500 bg-slate-800'
                          : 'border-slate-700 hover:border-slate-500 bg-slate-950/50'
                      }`}
                    >
                      <div
                        className={`font-bold mb-1.5 ${
                          choice === i ? 'text-amber-400' : 'text-slate-200'
                        }`}
                      >
                        {i + 1}. {opt.label}
                      </div>
                      <div className="text-slate-400 text-sm leading-relaxed">
                        {opt.description}
                      </div>
                    </button>
                  ))}
                </div>
              ) : (
                /* Freeform: textarea */
                <div>
                  <textarea
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="How do you respond? Type freely — the AI will interpret your decision and determine its consequences..."
                    rows={5}
                    className="w-full bg-slate-800 border border-slate-700 text-slate-100 p-4 resize-none focus:outline-none focus:border-amber-500 placeholder-slate-600 text-sm leading-relaxed"
                  />
                  <p className="text-slate-600 text-xs mt-1">Ctrl+Enter to submit</p>
                </div>
              )}

              {error && (
                <p className="text-red-400 text-sm mt-4 border border-red-900 bg-red-950/40 px-3 py-2">
                  {error}
                </p>
              )}

              <button
                onClick={handleSubmit}
                disabled={loading || !canSubmit}
                className="mt-5 bg-red-700 hover:bg-red-600 disabled:bg-slate-800 disabled:text-slate-600 text-white font-bold py-2.5 px-8 tracking-widest transition-colors text-sm"
              >
                SUBMIT DECISION →
              </button>
            </div>
          </main>
        </div>
      </div>
    </div>
  )
}
