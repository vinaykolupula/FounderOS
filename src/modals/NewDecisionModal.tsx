import { useState, useEffect } from 'react'
import { X, Check } from 'lucide-react'

export function NewDecisionModal({
  onClose,
  onSave,
}: {
  onClose: () => void
  onSave: (title: string, detail: string) => void
}) {
  const [title, setTitle] = useState('')
  const [detail, setDetail] = useState('')

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [onClose])

  return (
    <div
      className="modal-backdrop"
      role="presentation"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <section className="editor-modal" role="dialog" aria-modal="true">
        <div className="modal-header">
          <div>
            <p className="eyebrow">INSTITUTIONAL MEMORY</p>
            <h2>Record New Decision</h2>
          </div>
          <button className="icon-button" onClick={onClose} aria-label="Close modal">
            <X size={18} />
          </button>
        </div>
        <p className="modal-copy">
          Preserve decision choices, rationale, and review dates to prevent repeated debates.
        </p>
        <div className="form-grid single editor-fields">
          <label className="field">
            <span>Decision title</span>
            <input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Expand sales team into Europe"
            />
          </label>
          <label className="field">
            <span>Rationale & Detail</span>
            <input
              value={detail}
              onChange={(e) => setDetail(e.target.value)}
              placeholder="e.g. Customer demand is high, pipeline +24%"
            />
          </label>
        </div>
        <div className="modal-footer">
          <button className="secondary-button" onClick={onClose}>
            Cancel
          </button>
          <button
            className="primary-button"
            onClick={() => title && onSave(title, detail)}
          >
            Save decision <Check size={15} />
          </button>
        </div>
      </section>
    </div>
  )
}

