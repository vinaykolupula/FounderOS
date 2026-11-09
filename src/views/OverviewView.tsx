import {
  Sparkles,
  ArrowUpRight,
  RefreshCw,
  CircleAlert,
  ListChecks,
  ChevronRight,
  MoreHorizontal,
  ShieldCheck,
  Check,
  FileText,
} from 'lucide-react'
import { type CompanyProfile, type FounderProfile, type Workspace } from '../domain'
import { defaultSignals, type CompanySignal } from './IntelligenceView'

export function Focus({
  index,
  title,
  detail,
}: {
  index: string
  title: string
  detail: string
}) {
  return (
    <div className="focus-item">
      <span className="focus-index">{index}</span>
      <div>
        <strong>{title}</strong>
        <small>{detail}</small>
      </div>
      <ChevronRight size={16} />
    </div>
  )
}

export function OverviewView({
  company,
  founder,
  actions,
  signals = defaultSignals,
  onApprove,
  onPreview,
  onReviewSignal,
  onRefresh,
  briefUpdated,
  onViewIntelligence,
  onDebate,
  onInvestorUpdate,
}: {
  company: CompanyProfile
  founder: FounderProfile
  actions: Workspace['actions']
  signals?: CompanySignal[]
  onApprove: (id: number) => void
  onPreview: (action: any) => void
  onReviewSignal: (signal: any) => void
  onRefresh: () => void
  briefUpdated: boolean
  onViewIntelligence: () => void
  onDebate: () => void
  onInvestorUpdate: () => void
}) {
  return (
    <div className="page overview-page">
      <section className="welcome-row">
        <div>
          <p className="eyebrow">THURSDAY, AUGUST 7</p>
          <h1>Good morning, {founder.name || 'Founder'}.</h1>
          <p className="subhead">Here is what deserves your attention before you start your day.</p>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            className="secondary-button"
            onClick={onInvestorUpdate}
            style={{
              height: '38px',
              fontSize: '13px',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
            }}
          >
            👑 Investor Update
          </button>
          <button
            className={`refresh-button ${briefUpdated ? 'spinning' : ''}`}
            onClick={onRefresh}
          >
            <RefreshCw size={16} /> Refresh brief
          </button>
        </div>
      </section>

      <section className="health-strip">
        <div className="health-main">
          <div className="pulse-ring">
            <span>82</span>
          </div>
          <div>
            <p>COMPANY HEALTH</p>
            <strong>Focused, with one emerging risk</strong>
            <small>
              <span className="up">↗ 4 pts</span> from last week
            </small>
          </div>
        </div>
        <div className="health-divider" />
        <div className="health-stat">
          <span>Runway</span>
          <strong>
            {company.runwayMonths || 12} <small>mo</small>
          </strong>
          <i className="stable">On plan</i>
        </div>
        <div className="health-stat">
          <span>Critical alerts</span>
          <strong>02</strong>
          <i className="attention">Needs attention</i>
        </div>
        <div className="health-stat">
          <span>Momentum</span>
          <strong>Rising</strong>
          <i className="stable">+18% pipeline</i>
        </div>
      </section>

      <section className="grid-main">
        <article className="card recommendation-card">
          <div className="card-topline">
            <span className="section-kicker">
              <Sparkles size={14} /> CEO RECOMMENDATION
            </span>
            <button className="quiet-button" onClick={onDebate}>
              Executive Debate <ArrowUpRight size={14} />
            </button>
          </div>
          <div className="recommendation-content">
            <div className="recommendation-number">01</div>
            <div>
              <h2>Pause Feature B. Fix activation first.</h2>
              <p>
                Experiment B correlates with a 12% fall in{' '}
                {company.primaryConstraint || 'first-value completion'}. This is now the clearest constraint on new revenue.
              </p>
            </div>
          </div>
          <div className="evidence-grid">
            <div>
              <span>Evidence</span>
              <strong>3 independent signals</strong>
            </div>
            <div>
              <span>Confidence</span>
              <strong>High evidence</strong>
            </div>
            <div>
              <span>Decision review</span>
              <strong>Friday, 3:30 PM</strong>
            </div>
          </div>
          <div className="counterpoint">
            <CircleAlert size={16} />
            <span>
              <strong>Skeptic view:</strong> The decline could be seasonal. Use five customer interviews to rule this out.
            </span>
          </div>
        </article>

        <aside className="card focus-card">
          <div className="card-topline">
            <span className="section-kicker">
              <ListChecks size={14} /> TODAY'S FOCUS
            </span>
            <span className="count-pill">3 items</span>
          </div>
          <div className="focus-list">
            <div onClick={onDebate} style={{ cursor: 'pointer' }}>
              <Focus
                index="1"
                title="Approve activation investigation"
                detail="Unblocks Product and Engineering"
              />
            </div>
            <div onClick={() => onViewIntelligence()} style={{ cursor: 'pointer' }}>
              <Focus
                index="2"
                title="Join enterprise discovery call"
                detail="2:00 PM · Atlas Logistics"
              />
            </div>
            <div onClick={onDebate} style={{ cursor: 'pointer' }}>
              <Focus
                index="3"
                title="Review hiring plan"
                detail="Draft needs your judgment"
              />
            </div>
          </div>
        </aside>
      </section>

      <section className="section-header">
        <div>
          <h2>What changed</h2>
          <p>Signals ranked by potential impact on your goals.</p>
        </div>
        <button className="text-button" onClick={onViewIntelligence}>
          View intelligence <ChevronRight size={16} />
        </button>
      </section>

      <section className="signal-grid">
        {signals.map((signal) => (
          <article className={`signal-card ${signal.tone}`} key={signal.title}>
            <div className="signal-top">
              <span>{signal.tag}</span>
              <MoreHorizontal size={17} />
            </div>
            <h3>{signal.title}</h3>
            <p>{signal.body}</p>
            <button onClick={() => onReviewSignal(signal)}>
              Review signal <ArrowUpRight size={14} />
            </button>
          </article>
        ))}
      </section>

      <section className="section-header action-header">
        <div>
          <h2>Ready for your approval</h2>
          <p>FounderOS prepares work. You keep final control.</p>
        </div>
        <span className="approval-note">
          <ShieldCheck size={15} /> Approval required
        </span>
      </section>

      <section className="approval-list">
        {actions.length === 0 ? (
          <div className="empty-state">
            <Check size={20} /> Everything is cleared. FounderOS will surface the next action when it matters.
          </div>
        ) : (
          actions.map((action) => (
            <article className="approval-row" key={action.id}>
              <div className="approval-icon">
                <FileText size={18} />
              </div>
              <div className="approval-copy">
                <div>
                  <h3>{action.title}</h3>
                  <span className={`status ${action.status.toLowerCase()}`}>
                    {action.status}
                  </span>
                </div>
                <p>{action.detail}</p>
                <small>{action.source}</small>
              </div>
              <div className="approval-actions">
                <button className="secondary-button" onClick={() => onPreview(action)}>
                  Preview
                </button>
                <button className="primary-button" onClick={() => onApprove(action.id)}>
                  Approve <Check size={15} />
                </button>
              </div>
            </article>
          ))
        )}
      </section>
    </div>
  )
}

