import { ShieldCheck, X, Check } from 'lucide-react'

export function PreviewActionModal({
  action,
  onClose,
  onApprove,
}: {
  action: any
  onClose: () => void
  onApprove: (id: number) => void
}) {
  if (!action) return null

  return (
    <div
      className="modal-backdrop"
      role="presentation"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <section
        className="editor-modal"
        style={{ maxWidth: '540px' }}
        role="dialog"
        aria-modal="true"
      >
        <div className="modal-header">
          <div>
            <p className="eyebrow" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <ShieldCheck size={14} /> ACTION PREVIEW & POLICY CHECK
            </p>
            <h2>{action.title}</h2>
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
          <p style={{ margin: 0, fontSize: '13px', color: '#1e293b' }}>{action.detail}</p>
          <small
            style={{
              display: 'block',
              marginTop: '8px',
              color: '#64748b',
              fontFamily: 'var(--font-mono)',
            }}
          >
            Source Platform: {action.source}
          </small>
        </div>
        <div
          style={{
            background: '#dcfce7',
            padding: '10px 12px',
            borderRadius: '6px',
            border: '1px solid #86efac',
            color: '#15803d',
            fontSize: '12px',
            marginBottom: '16px',
          }}
        >
          <strong>Policy Engine Check:</strong> Passed domain allow-list and risk level verification. Draft dispatch enabled upon approval.
        </div>
        <div className="modal-footer">
          <button className="secondary-button" onClick={onClose}>
            Close preview
          </button>
          <button className="primary-button" onClick={() => onApprove(action.id)}>
            Approve & Dispatch <Check size={15} />
          </button>
        </div>
      </section>
    </div>
  )
}

