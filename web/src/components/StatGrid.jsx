/**
 * StatGrid — renders national stats, economy stats, and faction support as
 * labeled progress bars with colour-coded health indicators.
 *
 * Props:
 *   national  — national_stats dict from API
 *   economy   — economy_stats dict from API
 *   factions  — faction_support dict from API
 *   compact   — if true, render as a tighter single-column layout
 */

const NATIONAL_STATS = [
  { key: 'public_trust',             label: 'Public Trust',      inverted: false },
  { key: 'unrest',                   label: 'Unrest',            inverted: true  },
  { key: 'institutional_strength',   label: 'Institutions',      inverted: false },
  { key: 'media_freedom',            label: 'Media Freedom',     inverted: false },
  { key: 'international_reputation', label: "Int'l Reputation",  inverted: false },
]

const ECONOMY_STATS = [
  { key: 'stock_market',    label: 'Stock Market',    inverted: false },
  { key: 'unemployment',    label: 'Unemployment',    inverted: true  },
  { key: 'consumer_prices', label: 'Consumer Prices', inverted: true  },
  { key: 'budget_deficit',  label: 'Budget Deficit',  inverted: true  },
]

const FACTION_STATS = [
  { key: 'workers',                label: 'Workers',             inverted: false },
  { key: 'business_elite',         label: 'Business Elite',      inverted: false },
  { key: 'rural_bloc',             label: 'Rural Bloc',          inverted: false },
  { key: 'urban_progressives',     label: 'Urban Progressives',  inverted: false },
  { key: 'security_forces',        label: 'Security Forces',     inverted: false },
  { key: 'national_conservatives', label: 'Nat. Conservatives',  inverted: false },
]

function barColor(value, inverted) {
  const effective = inverted ? 100 - value : value
  if (effective >= 65) return 'bg-green-500'
  if (effective >= 35) return 'bg-yellow-500'
  return 'bg-red-500'
}

function textColor(value, inverted) {
  const effective = inverted ? 100 - value : value
  if (effective >= 65) return 'text-green-400'
  if (effective >= 35) return 'text-yellow-400'
  return 'text-red-400'
}

function StatBar({ label, value, inverted }) {
  const pct = Math.max(0, Math.min(100, value ?? 0))
  return (
    <div className="mb-2 last:mb-0">
      <div className="flex justify-between items-center mb-0.5">
        <span className="text-slate-400 text-xs">{label}</span>
        <span className={`font-mono text-xs font-bold ${textColor(pct, inverted)}`}>
          {pct}
        </span>
      </div>
      <div className="h-1.5 bg-slate-700 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-300 ${barColor(pct, inverted)}`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  )
}

function StatSection({ title, stats, data }) {
  return (
    <div className="bg-slate-900 border border-slate-800 p-4">
      <div className="text-xs text-slate-500 uppercase tracking-widest mb-3 font-bold">
        {title}
      </div>
      {stats.map(({ key, label, inverted }) => (
        <StatBar key={key} label={label} value={data?.[key] ?? 0} inverted={inverted} />
      ))}
    </div>
  )
}

export default function StatGrid({ national, economy, factions }) {
  return (
    <div className="space-y-3">
      <StatSection title="National" stats={NATIONAL_STATS} data={national} />
      <StatSection title="Economy"  stats={ECONOMY_STATS}  data={economy}  />
      <StatSection title="Factions" stats={FACTION_STATS}  data={factions} />
    </div>
  )
}
