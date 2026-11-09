import { useState, useEffect } from 'react'
import { Command, X, Send } from 'lucide-react'

export function AskFounderOSModal({
  onClose,
  onDebate,
}: {
  onClose: () => void
  onDebate: (query: string) => void
}) {
  const [prompt, setPrompt] = useState('')

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
      <section
        className="editor-modal"
        style={{ maxWidth: '580px' }}
        role="dialog"
        aria-modal="true"
      >
        <div className="modal-header">
          <div>
            <p className="eyebrow" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Command size={14} /> ASK FOUNDEROS
            </p>
            <h2>Direct Founder Reasoning Prompt</h2>
          </div>
          <button className="icon-button" onClick={onClose} aria-label="Close modal">
            <X size={18} />
          </button>
        </div>
        <p className="modal-copy">
          Query your operating workspace or prompt the Executive Board over any choice.
        </p>

        <div style={{ display: 'flex', gap: '8px', margin: '16px 0' }}>
          <input
            autoFocus
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="e.g. Should we expand our logistics wedge or focus on activation?"
            style={{
              flex: 1,
              padding: '12px 14px',
              borderRadius: '8px',
              border: '1px solid #cbd5e1',
              fontSize: '14px',
              outline: 'none',
            }}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && prompt.trim()) {
                onDebate(prompt)
              }
            }}
          />
          <button
            className="primary-button"
            onClick={() => prompt.trim() && onDebate(prompt)}
          >
            <Send size={15} /> Ask Board
          </button>
        </div>

        <div style={{ fontSize: '12px', color: '#64748b' }}>
          <strong>Suggested Prompts:</strong>
          <ul style={{ margin: '6px 0 0', paddingLeft: '18px', lineHeight: '1.6' }}>
            <li
              style={{ cursor: 'pointer', color: '#2563eb' }}
              onClick={() => onDebate('Pause Feature B and investigate activation')}
            >
              "Pause Feature B and investigate activation"
            </li>
            <li
              style={{ cursor: 'pointer', color: '#2563eb' }}
              onClick={() => onDebate('Should we hire a VP Sales for logistics outreach?')}
            >
              "Should we hire a VP Sales for logistics outreach?"
            </li>
          </ul>
        </div>
      </section>
    </div>
  )
}

