import { useState } from 'react'
import Modal from './Modal.jsx'

const GITHUB = 'https://github.com/mhughes72/fungame05'

// ── About ──────────────────────────────────────────────────────────────────────

function AboutContent() {
  return (
    <div className="space-y-5 text-slate-300 text-sm leading-relaxed">

      <a
        href={GITHUB}
        target="_blank"
        rel="noopener noreferrer"
        className="flex items-center gap-2 text-amber-400 hover:text-amber-300 transition-colors font-bold text-xs uppercase tracking-widest border border-amber-800 bg-amber-950/40 px-4 py-2 w-fit"
      >
        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z" />
        </svg>
        github.com/mhughes72/fungame05
      </a>

      <p>
        <span className="text-slate-100 font-bold">Republic of Veridia</span> is a turn-based
        political simulator. You govern a small, troubled fictional republic through twelve months
        of crises. Every decision shifts faction loyalty, national stability, and your grip on power
        — narrated by an LLM with a dark sense of humour.
      </p>

      <div>
        <div className="text-slate-400 text-xs uppercase tracking-widest mb-2 font-bold">Core design principle</div>
        <blockquote className="border-l-2 border-amber-600 pl-4 italic text-slate-400">
          Deterministic logic decides the bounds of truth. The LLM interprets faction attitudes
          inside those bounds.
        </blockquote>
        <p className="mt-2 text-slate-400 text-xs">
          The game engine owns all numerical outcomes. The LLM never writes directly to game state
          — it classifies reactions from a fixed vocabulary (loves_it → hates_it) and generates
          flavour text. In freeform mode it also proposes effects, but the engine clamps every value
          before applying it. Bad decisions have costs even if the player doesn't acknowledge them.
        </p>
      </div>

      <div>
        <div className="text-slate-400 text-xs uppercase tracking-widest mb-2 font-bold">The economy</div>
        <p className="text-slate-400 text-xs">
          Four sub-stats — stock market, unemployment, consumer prices, and budget deficit — drift
          autonomously every turn based on 12 conditional rules, passively dragging faction support
          up or down. The economy reacts to the world, not to decision labels. You can make the
          right political call and still watch the budget deteriorate because a recession was already
          in motion.
        </p>
      </div>

      <div>
        <div className="text-slate-400 text-xs uppercase tracking-widest mb-2 font-bold">Two modes</div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div className="bg-slate-800 border border-slate-700 p-3">
            <div className="text-slate-200 font-bold text-xs mb-1">Classic</div>
            <div className="text-slate-400 text-xs">12 authored crisis templates, pre-written options with hand-tuned effects. The AI adds a modifier layer on top based on each faction's mood and values.</div>
          </div>
          <div className="bg-slate-800 border border-slate-700 p-3">
            <div className="text-slate-200 font-bold text-xs mb-1">Freeform</div>
            <div className="text-slate-400 text-xs">AI generates each crisis as a causal consequence of your prior decisions. You respond in plain language. The AI evaluates what you actually did — not how confidently you phrased it.</div>
          </div>
        </div>
      </div>

      <div className="border-t border-slate-800 pt-4">
        <div className="text-slate-500 text-xs uppercase tracking-widest mb-2">Built with</div>
        <div className="flex flex-wrap gap-2">
          {['LangGraph', 'OpenAI', 'FastAPI', 'React', 'Vite', 'Tailwind CSS'].map(t => (
            <span key={t} className="text-slate-400 text-xs bg-slate-800 border border-slate-700 px-2 py-0.5">{t}</span>
          ))}
        </div>
      </div>

    </div>
  )
}

// ── Help ───────────────────────────────────────────────────────────────────────

function Section({ title, children }) {
  return (
    <div>
      <div className="text-amber-400 text-xs uppercase tracking-widest font-bold mb-2">{title}</div>
      {children}
    </div>
  )
}

function HelpContent() {
  return (
    <div className="space-y-6 text-slate-300 text-sm leading-relaxed">

      <Section title="Objective">
        <p>
          You are the newly elected leader of the Republic of Veridia. Survive twelve months in
          office without the country collapsing, the economy cratering, or your government losing
          all legitimacy. Each month a political crisis lands on your desk. Respond. Live with it.
        </p>
      </Section>

      <Section title="Turn structure">
        <ol className="list-decimal list-inside space-y-1 text-slate-400 text-xs">
          <li>Read the <span className="text-slate-200">situation briefing</span> — the AI describes the current political atmosphere</li>
          <li>Review your <span className="text-slate-200">stats</span> — national health, economy, faction support</li>
          <li>Read the <span className="text-slate-200">crisis</span> — something has gone wrong (again)</li>
          <li className="text-slate-300">Choose a response — numbered option (Classic) or free text (Freeform)</li>
          <li>Review the <span className="text-slate-200">consequences</span> — stat changes, advisor opinions, faction reactions, press coverage</li>
          <li>Repeat for 12 months</li>
        </ol>
      </Section>

      <Section title="Stats (all 0–100)">
        <div className="space-y-3">
          <div>
            <div className="text-slate-300 text-xs font-bold mb-1">National</div>
            <div className="space-y-1">
              {[
                ['Public Trust', 'Belief that you are competent and legitimate. Loss condition at 0.'],
                ['Unrest', 'Protests, disorder, street conflict. High is bad. Loss condition at 100.'],
                ['Institutional Strength', 'Courts, civil service, rule of law. Loss condition at 0.'],
                ['Media Freedom', 'Press independence. Low values push toward authoritarian end states.'],
                ["Int'l Reputation", 'Foreign relations and investor confidence.'],
              ].map(([name, desc]) => (
                <div key={name} className="flex gap-2">
                  <span className="text-slate-200 text-xs w-36 shrink-0">{name}</span>
                  <span className="text-slate-500 text-xs">{desc}</span>
                </div>
              ))}
            </div>
          </div>
          <div>
            <div className="text-slate-300 text-xs font-bold mb-1">Economy (drift autonomously every turn)</div>
            <div className="space-y-1">
              {[
                ['Stock Market', 'Investor confidence. Loss condition at 0.'],
                ['Unemployment', 'High = bad. Loss condition at 100. Passively drains Workers support.'],
                ['Consumer Prices', 'High = bad. Drains Workers and Rural Bloc support.'],
                ['Budget Deficit', 'High = bad. Fiscal recklessness erodes business confidence.'],
              ].map(([name, desc]) => (
                <div key={name} className="flex gap-2">
                  <span className="text-slate-200 text-xs w-36 shrink-0">{name}</span>
                  <span className="text-slate-500 text-xs">{desc}</span>
                </div>
              ))}
            </div>
          </div>
          <div>
            <div className="text-slate-300 text-xs font-bold mb-1">Factions (6 groups)</div>
            <p className="text-slate-500 text-xs">
              Workers · Business Elite · Rural Bloc · Urban Progressives · Security Forces · National Conservatives.
              Each has values, grievances, and a mood that shapes how they react to your decisions.
              Their support feeds into threshold events and your final end-state classification.
            </p>
          </div>
        </div>
      </Section>

      <Section title="How you lose">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-1">
          {[
            'Public Trust → 0',
            'Unrest → 100',
            'Stock Market → 0',
            'Unemployment → 100',
            'Institutional Strength → 0',
          ].map(c => (
            <div key={c} className="text-red-400 text-xs flex gap-1.5 items-center">
              <span className="text-red-700">✗</span> {c}
            </div>
          ))}
        </div>
      </Section>

      <Section title="Threshold events">
        <p className="text-slate-400 text-xs mb-2">
          When multiple stats drift into dangerous territory simultaneously, a cascading event fires
          automatically — once per game. These are punishments for neglect, not decisions.
        </p>
        <div className="space-y-1">
          {[
            ['Coup Attempt', 'Security Forces low + high Unrest + weak Institutions'],
            ['General Strike', 'Workers very low + high Unrest'],
            ['Capital Flight', 'Business Elite very low + weak Stock Market'],
            ['Constitutional Crisis', 'Very weak Institutions + low Public Trust'],
            ['Mass Protest', 'Urban Progressives low + suppressed Media + high Unrest'],
          ].map(([name, cond]) => (
            <div key={name} className="flex gap-2">
              <span className="text-yellow-500 text-xs w-36 shrink-0 font-bold">{name}</span>
              <span className="text-slate-500 text-xs">{cond}</span>
            </div>
          ))}
        </div>
      </Section>

      <Section title="How you win & end states">
        <p className="text-slate-400 text-xs mb-2">
          Survive all 12 months. Your final stats determine which kind of leader you were.
        </p>
        <div className="space-y-1">
          {[
            ['Reformist Survivor', 'High trust, strong institutions, free press'],
            ['Business-Backed Technocrat', 'Strong markets, business elite happy, low deficit'],
            ['Populist Strongman', 'Low media freedom, national conservatives loyal, low unrest'],
            ['Authoritarian Ruler', 'Suppressed media, very weak institutions'],
            ['Crisis Manager', 'Low unrest, some trust — survived by presence, not vision'],
            ['Failed Democrat', 'Everything else'],
          ].map(([name, cond]) => (
            <div key={name} className="flex gap-2">
              <span className="text-slate-200 text-xs w-44 shrink-0 font-bold">{name}</span>
              <span className="text-slate-500 text-xs">{cond}</span>
            </div>
          ))}
        </div>
      </Section>

      <Section title="Classic vs Freeform">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div className="bg-slate-800 border border-slate-700 p-3">
            <div className="text-slate-200 font-bold text-xs mb-2">Classic mode</div>
            <ul className="text-slate-400 text-xs space-y-1 list-disc list-inside">
              <li>12 authored crisis templates</li>
              <li>3–4 numbered options per crisis</li>
              <li>Effects are pre-written, balanced</li>
              <li>AI adds a ±1–3 modifier based on faction mood</li>
              <li>More predictable, easier to plan around</li>
            </ul>
          </div>
          <div className="bg-slate-800 border border-slate-700 p-3">
            <div className="text-slate-200 font-bold text-xs mb-2">Freeform mode</div>
            <ul className="text-slate-400 text-xs space-y-1 list-disc list-inside">
              <li>AI generates crises from your decision history</li>
              <li>Type anything — the AI evaluates it</li>
              <li>Effects are AI-proposed, engine-clamped</li>
              <li>Narrative continuity builds across turns</li>
              <li>Unpredictable. Consequences are real.</li>
            </ul>
          </div>
        </div>
      </Section>

    </div>
  )
}

// ── Cheat ──────────────────────────────────────────────────────────────────────

function CheatContent() {
  return (
    <div className="text-center py-8 space-y-4">
      <div className="text-red-600 text-4xl font-black tracking-widest">■</div>
      <div className="text-slate-500 text-xs uppercase tracking-widest">CLASSIFIED</div>
      <p className="text-slate-300 font-bold text-lg">Coming soon...</p>
      <p className="text-slate-600 text-xs italic max-w-xs mx-auto">
        The Ministry of Information is still preparing this document.
        Some redactions remain pending.
      </p>
    </div>
  )
}

// ── NavButtons (exported) ──────────────────────────────────────────────────────

function NavBtn({ onClick, children }) {
  return (
    <button
      onClick={onClick}
      className="text-slate-500 hover:text-slate-300 text-xs uppercase tracking-widest transition-colors px-1"
    >
      {children}
    </button>
  )
}

export default function NavButtons() {
  const [modal, setModal] = useState(null)
  const close = () => setModal(null)

  return (
    <>
      <div className="flex gap-4">
        <NavBtn onClick={() => setModal('about')}>About</NavBtn>
        <NavBtn onClick={() => setModal('help')}>Help</NavBtn>
        <NavBtn onClick={() => setModal('cheat')}>Cheat</NavBtn>
      </div>

      {modal === 'about' && (
        <Modal title="About — Republic of Veridia" onClose={close} wide>
          <AboutContent />
        </Modal>
      )}
      {modal === 'help' && (
        <Modal title="How to Play" onClose={close} wide>
          <HelpContent />
        </Modal>
      )}
      {modal === 'cheat' && (
        <Modal title="Cheat Codes" onClose={close}>
          <CheatContent />
        </Modal>
      )}
    </>
  )
}
