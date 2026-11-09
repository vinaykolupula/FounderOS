import { useEffect } from 'react'
import { Sun, X, CheckCircle2, ArrowUpRight, Check } from 'lucide-react'

export function MorningBriefingModal({
  data,
  onClose,
  onDebate,
}: {
  data: any
  onClose: () => void
  onDebate: (title: string) => void
}) {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [onClose])

  if (!data) return null

  return (
    <div
      className="modal-backdrop"
      role="presentation"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <section
        className="editor-modal"
        style={{ maxWidth: '680px', maxHeight: '85vh', overflowY: 'auto' }}
        role="dialog"
        aria-modal="true"
      >
        <div className="modal-header">
          <div>
            <p className="eyebrow" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Sun size={14} style={{ color: '#d97706' }} />
              <span>EXECUTIVE MORNING BRIEFING</span>
            </p>
            <h2>{data.date || "Today's Briefing"}</h2>
          </div>
          <button className="icon-button" onClick={onClose} aria-label="Close modal">
            <X size={18} />
          </button>
        </div>

        <div
          style={{
            background: '#f8fafc',
            padding: '14px 16px',
            borderRadius: '10px',
            border: '1px solid #e2e8f0',
            margin: '14px 0',
          }}
        >
          <strong style={{ color: '#0f172a', fontSize: '0.85rem' }}>Executive Overview</strong>
          <p style={{ margin: '6px 0 0', fontSize: '0.88rem', color: '#334155', lineHeight: '1.5' }}>
            {data.executiveSummary}
          </p>
        </div>

        <div style={{ margin: '14px 0' }}>
          <span className="section-kicker" style={{ fontSize: '11px', color: '#64748b' }}>
            OVERNIGHT HIGHLIGHTS & SIGNAL SYNTHESIS
          </span>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '6px' }}>
            {data.overnightChanges?.map((item: string, idx: number) => (
              <div
                key={idx}
                style={{
                  background: '#ffffff',
                  padding: '10px 14px',
                  borderRadius: '8px',
                  border: '1px solid #e2e8f0',
                  fontSize: '12px',
                  color: '#1e293b',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                }}
              >
                <CheckCircle2 size={14} style={{ color: '#16a34a', flexShrink: 0 }} />
                <span>{item}</span>
              </div>
            ))}
          </div>
        </div>

        <div
          style={{
            background: '#eff6ff',
            padding: '12px 14px',
            borderRadius: '8px',
            border: '1px solid #bfdbfe',
            color: '#1e40af',
            fontSize: '12px',
            margin: '12px 0',
          }}
        >
          <strong>One Metric That Matters (OMTM):</strong> {data.omtmStatus}
        </div>

        <div
          style={{
            background: '#f0fdf4',
            padding: '14px',
            borderRadius: '8px',
            border: '1px solid #bbf7d0',
            color: '#15803d',
            fontSize: '12px',
            margin: '12px 0',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <div>
            <strong>Today's Highest Leverage Focus:</strong>
            <div style={{ fontSize: '13px', fontWeight: 700, color: '#166534', marginTop: '2px' }}>
              {data.topPriorityFocus}
            </div>
          </div>
          <button
            className="primary-button"
            style={{ fontSize: '11px', padding: '6px 12px' }}
            onClick={() => {
              onClose()
              onDebate(data.topPriorityFocus)
            }}
          >
            Debate Action <ArrowUpRight size={12} />
          </button>
        </div>

        {data.energyAdvice && (
          <div
            style={{
              background: '#fefce8',
              padding: '10px 14px',
              borderRadius: '8px',
              border: '1px solid #fef08a',
              color: '#854d0e',
              fontSize: '11px',
              margin: '10px 0',
            }}
          >
            <strong>Psychological Energy Guide:</strong> {data.energyAdvice}
          </div>
        )}

        <div className="modal-footer" style={{ marginTop: '16px' }}>
          <button className="primary-button" onClick={onClose}>
            Acknowledge & Start Day <Check size={15} />
          </button>
        </div>
      </section>
    </div>
  )
}

