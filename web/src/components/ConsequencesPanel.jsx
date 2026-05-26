import StatGrid from './StatGrid.jsx'

// Stats where a positive delta = bad (displayed in red)
const INVERTED = new Set(['unrest', 'unemployment', 'consumer_prices', 'budget_deficit'])

const EFFECT_LABELS = {
  public_trust:             'Public Trust',
  unrest:                   'Unrest',
  institutional_strength:   'Institutions',
  media_freedom:            'Media Freedom',
  international_reputation: "Int'l Rep.",
  stock_market:             'Stock Market',
  unemployment:             'Unemployment',
  consumer_prices:          'Consumer Prices',
  budget_deficit:           'Budget Deficit',
  workers:                  'Workers',
  business_elite:           'Business Elite',
  rural_bloc:               'Rural Bloc',
  urban_progressives:       'Urban Progressives',
  security_forces:          'Security Forces',
  national_conservatives:   'Nat. Conservatives',
}

const FACTION_NAMES = {
  workers:                'Workers',
  business_elite:         'Business Elite',
  rural_bloc:             'Rural Bloc',
  urban_progressives:     'Urban Progressives',
  security_forces:        'Security Forces',
  national_conservatives: 'National Conservatives',
}

function Delta({ value, statKey }) {
  if (value === 0 || value == null) return <span className="text-slate-600">—</span>
  const inverted = INVERTED.has(statKey)
  const isGood   = inverted ? value < 0 : value > 0
  const color    = isGood ? 'text-green-400' : 'text-red-400'
  return (
    <span className={`font-mono font-bold ${color}`}>
      {value > 0 ? `+${value}` : value}
    </span>
  )
}

function EffectsBlock({ title, effects }) {
  const nonZero = Object.entries(effects ?? {}).filter(([, v]) => v !== 0)
  if (nonZero.length === 0) return null
  return (
    <div>
      <div className="text-xs text-slate-500 uppercase tracking-widest mb-2 font-bold">{title}</div>
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-x-4 gap-y-1">
        {nonZero.map(([key, val]) => (
          <div key={key} className="flex justify-between items-center">
            <span className="text-slate-400 text-sm">{EFFECT_LABELS[key] ?? key}</span>
            <Delta value={val} statKey={key} />
          </div>
        ))}
      </div>
    </div>
  )
}

export default function ConsequencesPanel({ gameData, onContinue }) {
  const cons    = gameData.consequences ?? {}
  const isOver  = gameData.game_status !== 'active'
  // current_turn was incremented; the turn that just resolved was current_turn - 1
  const resolvedTurn = (gameData.current_turn ?? 1) - 1

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Top bar */}
      <div className="bg-slate-900 border-b border-slate-800 px-4 py-3 flex items-center justify-between sticky top-0 z-10">
        <div className="text-red-600 font-black tracking-widest text-sm">■ VERIDIA</div>
        <div className="text-slate-400 text-sm">
          MONTH <span className="text-slate-200 font-bold">{resolvedTurn}</span> RESOLVED
        </div>
      </div>

      <div className="max-w-3xl mx-auto p-4 lg:p-6 space-y-6">

        {/* Decision summary */}
        <div className="bg-slate-900 border-l-4 border-red-700 p-5">
          <div className="text-xs text-slate-500 uppercase tracking-widest mb-3 font-bold">
            Decision
          </div>
          {gameData.mode !== 'freeform' ? (
            <div className="text-slate-100 font-bold text-lg">
              {cons.selected_option_label ?? '—'}
            </div>
          ) : (
            <div className="space-y-2">
              {cons.player_input && (
                <p className="text-slate-300 italic text-sm">
                  &ldquo;{cons.player_input}&rdquo;
                </p>
              )}
              {cons.decision_interpretation && (
                <>
                  <div className="text-xs text-slate-500 uppercase tracking-widest pt-1">
                    Read as
                  </div>
                  <p className="text-slate-200">{cons.decision_interpretation}</p>
                </>
              )}
            </div>
          )}
        </div>

        {/* Stat effects */}
        {(Object.values(cons.final_stat_effects ?? {}).some(v => v !== 0) ||
          Object.values(cons.final_economy_effects ?? {}).some(v => v !== 0) ||
          Object.values(cons.final_faction_effects ?? {}).some(v => v !== 0)) && (
          <div className="bg-slate-900 border border-slate-800 p-5 space-y-4">
            <div className="text-xs text-slate-500 uppercase tracking-widest font-bold">
              Effects
            </div>
            <EffectsBlock title="National Stats"   effects={cons.final_stat_effects} />
            <EffectsBlock title="Economy"          effects={cons.final_economy_effects} />
            <EffectsBlock title="Faction Support"  effects={cons.final_faction_effects} />
          </div>
        )}

        {/* Threshold events */}
        {(cons.triggered_events?.length ?? 0) > 0 && (
          <div className="bg-red-950 border border-red-800 p-5">
            <div className="text-red-400 font-bold text-xs uppercase tracking-widest mb-3">
              ⚠ Crisis Events Triggered
            </div>
            {cons.triggered_events.map(e => (
              <div key={e} className="mb-1">
                <span className="text-red-300 font-bold text-sm">
                  {e.replace(/_/g, ' ').toUpperCase()}
                </span>
              </div>
            ))}
          </div>
        )}

        {/* Advisor reactions */}
        {(cons.advisor_reactions?.length ?? 0) > 0 && (
          <div>
            <div className="text-xs text-slate-500 uppercase tracking-widest mb-3 font-bold">
              Advisor Reactions
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {cons.advisor_reactions.map((a, i) => (
                <div key={i} className="bg-slate-900 border border-slate-800 p-4">
                  <div className="text-amber-400 text-xs font-bold uppercase tracking-wide mb-2">
                    {a.name}
                  </div>
                  <p className="text-slate-300 text-sm italic leading-relaxed">
                    &ldquo;{a.reaction}&rdquo;
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Faction public statements */}
        {Object.keys(cons.faction_narrative ?? {}).length > 0 && (
          <div>
            <div className="text-xs text-slate-500 uppercase tracking-widest mb-3 font-bold">
              Public Statements
            </div>
            <div className="space-y-2.5">
              {Object.entries(cons.faction_narrative).map(([fid, text]) => (
                <div key={fid} className="flex gap-3">
                  <span className="text-slate-500 text-xs font-bold shrink-0 w-32 mt-0.5">
                    {FACTION_NAMES[fid] ?? fid}
                  </span>
                  <p className="text-slate-300 text-sm italic leading-relaxed">
                    &ldquo;{text}&rdquo;
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Headlines */}
        {(cons.headlines?.length ?? 0) > 0 && (
          <div>
            <div className="text-xs text-slate-500 uppercase tracking-widest mb-3 font-bold">
              The Press
            </div>
            <div className="space-y-2">
              {cons.headlines.map((h, i) => (
                <div key={i} className="bg-slate-900 border border-slate-800 p-3">
                  <div className="text-slate-500 text-xs italic mb-1">
                    {h.outlet ?? ''}
                  </div>
                  <div className="text-slate-200 font-bold text-sm">
                    {h.headline ?? ''}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Updated stats */}
        <div>
          <div className="text-xs text-slate-500 uppercase tracking-widest mb-3 font-bold">
            Current State of Veridia
          </div>
          <StatGrid
            national={gameData.national_stats}
            economy={gameData.economy_stats}
            factions={gameData.faction_support}
          />
        </div>

        {/* Continue / verdict button */}
        <div className="pb-8 pt-2">
          <button
            onClick={onContinue}
            className="bg-red-700 hover:bg-red-600 text-white font-bold py-3 px-10 text-base tracking-widest transition-colors"
          >
            {isOver ? 'SEE VERDICT →' : 'NEXT MONTH →'}
          </button>
        </div>

      </div>
    </div>
  )
}
