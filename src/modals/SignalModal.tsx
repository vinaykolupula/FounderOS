import { LineChart, X, ArrowUpRight } from 'lucide-react'

export function SignalModal({
  signal,
  onClose,
  onDebate,
}: {
  signal: any
  onClose: () => void
  onDebate: (title: string) => void
}) {
  if (!signal) return null

  return (
    <div
      className="modal-backdrop"
      role="presentation"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <section
        className="editor-modal"
        style={{ maxWidth: '520px' }}
        role="dialog"
        aria-modal="true"
      >
        <div className="modal-header">
          <div>
            <p className="eyebrow" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <LineChart size={14} /> SIGNAL ANALYSIS
            </p>
            <h2>{signal.title}</h2>
          </div>
          <button className="icon-button" onClick={onClose} aria-label="Close modal">
            <X size={18} />
          </button>
        </div>
        <div
          style={{
            background: '#f8fafc',
            padding: '14px',
            borderRadius: '8px',
            border: '1px solid #e2e8f0',
            margin: '14px 0',
          }}
        >
          <p style={{ margin: 0, fontSize: '13px', color: '#1e293b' }}>{signal.body}</p>
          <small style={{ display: 'block', marginTop: '8px', color: '#64748b' }}>
            Signal Category: <strong>{signal.tag}</strong>
          </small>
        </div>
        <div className="modal-footer">
          <button className="secondary-button" onClick={onClose}>
            Dismiss
          </button>
          <button
            className="primary-button"
            onClick={() => onDebate(signal.title)}
          >
            Debate Signal Impact <ArrowUpRight size={15} />
          </button>
        </div>
      </section>
    </div>
  )
}

