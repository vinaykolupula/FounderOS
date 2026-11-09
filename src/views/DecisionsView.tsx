import { Plus, ChevronRight } from 'lucide-react'
import { type Workspace } from '../domain'

export function Ledger({
  id,
  title,
  detail,
  status,
}: {
  id: string
  title: string
  detail: string
  status: string
}) {
  const statusClass = status.toLowerCase().includes('open')
    ? 'open'
    : status.toLowerCase().includes('validated')
    ? 'validated'
    : 'learning'

  return (
    <div className="ledger-row">
      <span className="decision-id">{id}</span>
      <div>
        <h3>{title}</h3>
        <p>{detail}</p>
      </div>
      <span className={`decision-status ${statusClass}`}>{status}</span>
      <ChevronRight size={18} />
    </div>
  )
}

export function DecisionsView({
  decisions,
  onOpenDebate,
  onNewDecision,
}: {
  decisions: Workspace['decisions']
  onOpenDebate: (title: string) => void
  onNewDecision: () => void
}) {
  const displayDecisions =
    decisions && decisions.length > 0
      ? decisions
      : [
          {
            id: 1,
            decisionCode: '#024',
            title: 'Pause Feature B and investigate activation',
            detail: 'Decision due Friday · High evidence · Click to debate',
            status: 'Open',
          },
          {
            id: 2,
            decisionCode: '#023',
            title: 'Focus enterprise outreach on logistics',
            detail: 'Decided July 28 · Pipeline +18% · Click to debate',
            status: 'Validated',
          },
          {
            id: 3,
            decisionCode: '#022',
            title: 'Move support ownership into Product',
            detail: 'Decided July 14 · Review Aug 14 · Click to debate',
            status: 'Learning',
          },
        ]

  return (
    <div className="page simple-page">
      <div className="simple-heading">
        <div>
          <p className="eyebrow">INSTITUTIONAL MEMORY</p>
          <h1>Decision ledger</h1>
          <p className="subhead">
            A record of choices, assumptions, and learning. Click any decision to trigger an AI Executive Board debate.
          </p>
        </div>
        <button className="primary-button" onClick={onNewDecision}>
          <Plus size={16} /> New decision
        </button>
      </div>
      <div className="ledger-card">
        {displayDecisions.map((d: any) => (
          <div
            key={d.id}
            onClick={() => onOpenDebate(d.title)}
            style={{ cursor: 'pointer' }}
          >
            <Ledger
              id={d.decisionCode || `#0${d.id}`}
              title={d.title}
              detail={d.detail}
              status={d.status || 'Open'}
            />
          </div>
        ))}
      </div>
    </div>
  )
}

