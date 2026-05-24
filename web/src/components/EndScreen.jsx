import StatGrid from './StatGrid.jsx'

export default function EndScreen({ gameData, onRestart }) {
  const won = gameData.game_status === 'won'

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Top bar */}
      <div className="bg-slate-900 border-b border-slate-800 px-4 py-3">
        <div className="text-red-600 font-black tracking-widest text-sm">■ VERIDIA</div>
      </div>

      <div className="max-w-3xl mx-auto p-4 lg:p-6 space-y-6">

        {/* Verdict banner */}
        <div
          className={`border-l-4 p-6 bg-slate-900 ${
            won ? 'border-green-500' : 'border-red-600'
          }`}
        >
          <div
            className={`text-4xl font-black mb-3 tracking-wider ${
              won ? 'text-green-400' : 'text-red-400'
            }`}
          >
            {won ? 'SURVIVED' : 'FALLEN'}
          </div>
          <div className="text-amber-400 text-2xl font-bold mb-4">
            {gameData.end_state ?? 'Failed Democrat'}
          </div>
          {gameData.loss_reason && (
            <p className="text-slate-400 italic leading-relaxed text-sm">
              {gameData.loss_reason}
            </p>
          )}
        </div>

        {/* Historical record / end summary */}
        {gameData.end_summary && (
          <div className="bg-slate-900 border border-slate-800 p-6">
            <div className="text-xs text-slate-500 uppercase tracking-widest mb-4 font-bold">
              Historical Record
            </div>
            <p className="text-slate-300 leading-relaxed italic">
              {gameData.end_summary}
            </p>
          </div>
        )}

        {/* Final stats */}
        <div>
          <div className="text-xs text-slate-500 uppercase tracking-widest mb-3 font-bold">
            Final State of Veridia
          </div>
          <StatGrid
            national={gameData.national_stats}
            economy={gameData.economy_stats}
            factions={gameData.faction_support}
          />
        </div>

        {/* Play again */}
        <div className="pb-8 pt-2 flex gap-4 items-center">
          <button
            onClick={onRestart}
            className="bg-slate-700 hover:bg-slate-600 text-white font-bold py-3 px-10 text-base tracking-widest transition-colors"
          >
            PLAY AGAIN
          </button>
          <p className="text-slate-600 text-xs italic">Veridia endures. Somehow.</p>
        </div>

      </div>
    </div>
  )
}
