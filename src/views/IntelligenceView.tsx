import { Plus, LineChart, Bell } from 'lucide-react'

export interface CompanySignal {
  title: string
  body: string
  tag: string
  tone: 'green' | 'orange' | 'purple' | 'blue'
}

export const defaultSignals: CompanySignal[] = [
  {
    title: 'Logistics customer mentions',
    body: 'Atlas Freight and two mid-market prospects completed onboarding calls praising the enterprise dashboard wedge.',
    tag: 'Customer Signals',
    tone: 'green',
  },
  {
    title: 'Activation completion below 60%',
    body: 'First-value onboarding completion fell 12% after the complex setup experiment rolled out.',
    tag: 'Product Analytics',
    tone: 'orange',
  },
  {
    title: 'Enterprise competitor pricing changes',
    body: 'Primary market competitor increased their minimum enterprise contract tier to $24k/yr.',
    tag: 'Market Intelligence',
    tone: 'purple',
  },
]

export function IntelligenceView({
  signals = defaultSignals,
  onSelectSignal,
}: {
  signals?: CompanySignal[]
  onSelectSignal: (s: CompanySignal) => void
}) {
  return (
    <div className="page simple-page">
      <div className="simple-heading">
        <div>
          <p className="eyebrow">OBSERVATION LAYER</p>
          <h1>Company intelligence</h1>
          <p className="subhead">Signals are ranked by impact, then connected to goals and decisions.</p>
        </div>
        <button
          className="secondary-button"
          onClick={() => onSelectSignal(signals[0])}
        >
          <Plus size={16} /> Add watchlist
        </button>
      </div>
      <div className="intel-layout">
        <article className="card intel-card">
          <span className="section-kicker">
            <LineChart size={14} /> OPPORTUNITY RADAR
          </span>
          <h2>Logistics is becoming your clearest wedge.</h2>
          <p>
            Three qualified opportunities, two recent customer requests, and a competitor gap point to a focused enterprise test.
          </p>
          <div className="radar-score">
            <span>Opportunity score</span>
            <strong>
              78 <small>/ 100</small>
            </strong>
          </div>
        </article>
        <article className="card watch-card">
          <span className="section-kicker">
            <Bell size={14} /> WATCHLIST
          </span>
          <div
            className="watch-item"
            style={{ cursor: 'pointer' }}
            onClick={() => onSelectSignal(signals[2])}
          >
            <span className="watch-dot purple" />
            Enterprise competitor pricing changes
          </div>
          <div
            className="watch-item"
            style={{ cursor: 'pointer' }}
            onClick={() => onSelectSignal(signals[1])}
          >
            <span className="watch-dot orange" />
            Activation completion below 60%
          </div>
          <div
            className="watch-item"
            style={{ cursor: 'pointer' }}
            onClick={() => onSelectSignal(signals[0])}
          >
            <span className="watch-dot green" />
            Logistics customer mentions
          </div>
        </article>
      </div>
    </div>
  )
}

