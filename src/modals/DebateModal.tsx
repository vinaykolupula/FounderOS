import { useEffect, useState } from 'react'
import { Sparkles, X, Compass, FlaskConical, AlertTriangle, ShieldCheck, Zap, Swords, Target, Skull } from 'lucide-react'

interface DialecticCritique {
  pair: string
  topic: string
  challenger: string
  defender: string
  critique: string
  rebuttal: string
  synthesis: string
}

interface ExecutivePerspective {
  lens: string
  stance: 'Support' | 'Oppose' | 'Caution'
  mentalModel?: string
  argument: string
  keyMetric: string
}

export interface DebateData {
  decisionTitle: string
  decisionFramework?: string
  executivePerspectives?: ExecutivePerspective[]
  dialecticCritiques?: DialecticCritique[]
  keyTradeoff?: string
  recommendedExperiment?: string
  oneMetricThatMatters?: string
  killCriteria?: string
  consensus?: 'STRONG GO' | 'CONDITIONAL GO' | 'HIGH RISK / PAUSE' | string
  confidence?: 'High' | 'Medium' | 'Low' | string
  isStreaming?: boolean
  currentStage?: string
}

export function DebateModal({
  data,
  onClose,
}: {
  data: DebateData | null
  onClose: () => void
}) {
  const [activeTab, setActiveTab] = useState<'all' | 'stances' | 'dialectic' | 'synthesis'>('all')

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [onClose])

  if (!data) return null

  const perspectives = data.executivePerspectives || []
  const dialectics = data.dialecticCritiques || []

  return (
    <div
      className="modal-backdrop"
      role="presentation"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <section
        className="editor-modal"
        style={{ maxWidth: '780px', maxHeight: '88vh', overflowY: 'auto' }}
        role="dialog"
        aria-modal="true"
      >
        {/* Header */}
        <div className="modal-header">
          <div>
            <p className="eyebrow" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Sparkles size={14} style={{ color: '#6366f1' }} />
              <span>PEAK MULTI-AGENT C-SUITE DIALECTIC DEBATE</span>
            </p>
            <h2 style={{ fontSize: '1.25rem', marginTop: '4px' }}>{data.decisionTitle}</h2>
          </div>
          <button className="icon-button" onClick={onClose} aria-label="Close modal">
            <X size={18} />
          </button>
        </div>

        {/* Streaming Banner */}
        {data.isStreaming && (
          <div
            style={{
              background: '#eff6ff',
              border: '1px solid #bfdbfe',
              padding: '10px 14px',
              borderRadius: '8px',
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              margin: '12px 0',
              color: '#1d4ed8',
              fontSize: '13px',
              fontWeight: 600,
            }}
          >
            <Zap size={16} className="animate-spin" style={{ color: '#2563eb' }} />
            <span>{data.currentStage || 'Live C-Suite board debate streaming...'}</span>
          </div>
        )}

        {/* Framework & Filter Navigation */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', margin: '12px 0', flexWrap: 'wrap', gap: '8px' }}>
          {data.decisionFramework && (
            <div
              style={{
                background: '#f1f5f9',
                padding: '6px 12px',
                borderRadius: '6px',
                fontSize: '11px',
                fontWeight: 600,
                color: '#475569',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
              }}
            >
              <Compass size={13} style={{ color: '#2563eb' }} />
              <span>Framework: <strong>{data.decisionFramework}</strong></span>
            </div>
          )}

          <div style={{ display: 'flex', gap: '4px' }}>
            <button
              className={`pill-button ${activeTab === 'all' ? 'active' : ''}`}
              style={{ fontSize: '11px', padding: '4px 10px' }}
              onClick={() => setActiveTab('all')}
            >
              Full Board Brief
            </button>
            <button
              className={`pill-button ${activeTab === 'stances' ? 'active' : ''}`}
              style={{ fontSize: '11px', padding: '4px 10px' }}
              onClick={() => setActiveTab('stances')}
            >
              Stances ({perspectives.length})
            </button>
            <button
              className={`pill-button ${activeTab === 'dialectic' ? 'active' : ''}`}
              style={{ fontSize: '11px', padding: '4px 10px' }}
              onClick={() => setActiveTab('dialectic')}
            >
              Cross-Exam Dialectics ({dialectics.length})
            </button>
            <button
              className={`pill-button ${activeTab === 'synthesis' ? 'active' : ''}`}
              style={{ fontSize: '11px', padding: '4px 10px' }}
              onClick={() => setActiveTab('synthesis')}
            >
              CEO Synthesis
            </button>
          </div>
        </div>

        {/* Round 1: C-Suite Perspectives */}
        {(activeTab === 'all' || activeTab === 'stances') && perspectives.length > 0 && (
          <div style={{ margin: '14px 0' }}>
            <h3 style={{ fontSize: '0.85rem', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '8px' }}>
              Round 1: Independent C-Suite Perspectives
            </h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '10px' }}>
              {perspectives.map((item) => (
                <div
                  key={item.lens}
                  style={{
                    background: '#ffffff',
                    padding: '12px 14px',
                    borderRadius: '8px',
                    border: '1px solid #e2e8f0',
                    boxShadow: '0 1px 2px rgba(0,0,0,0.03)',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                    <strong style={{ color: '#0f172a', fontSize: '0.84rem' }}>{item.lens}</strong>
                    <span
                      style={{
                        color: item.stance === 'Support' ? '#15803d' : item.stance === 'Oppose' ? '#b91c1c' : '#b45309',
                        fontSize: '0.75rem',
                        fontWeight: 700,
                        padding: '2px 6px',
                        borderRadius: '4px',
                        background: item.stance === 'Support' ? '#dcfce7' : item.stance === 'Oppose' ? '#fee2e2' : '#fef3c7',
                      }}
                    >
                      {item.stance}
                    </span>
                  </div>
                  {item.mentalModel && (
                    <div style={{ fontSize: '11px', color: '#64748b', marginBottom: '6px' }}>
                      🧠 {item.mentalModel}
                    </div>
                  )}
                  <p style={{ margin: '4px 0 8px', fontSize: '0.82rem', color: '#334155', lineHeight: '1.4' }}>
                    {item.argument}
                  </p>
                  <div style={{ fontSize: '11px', color: '#64748b', background: '#f8fafc', padding: '4px 8px', borderRadius: '4px', border: '1px solid #f1f5f9' }}>
                    <strong>Key Metric:</strong> {item.keyMetric}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Round 2: Adversarial Dialectic Cross-Examinations */}
        {(activeTab === 'all' || activeTab === 'dialectic') && dialectics.length > 0 && (
          <div style={{ margin: '16px 0' }}>
            <h3 style={{ fontSize: '0.85rem', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Swords size={14} style={{ color: '#dc2626' }} />
              Round 2: Cross-Examination Dialectic Tensions
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {dialectics.map((d, idx) => (
                <div
                  key={idx}
                  style={{
                    background: '#fcfcfd',
                    padding: '14px 16px',
                    borderRadius: '8px',
                    border: '1px solid #e0e7ff',
                    borderLeft: '4px solid #6366f1',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <div style={{ fontWeight: 700, color: '#312e81', fontSize: '0.85rem' }}>
                      {d.pair}: <span style={{ fontWeight: 500, color: '#4338ca' }}>{d.topic}</span>
                    </div>
                  </div>

                  {/* Critique */}
                  <div style={{ background: '#fef2f2', border: '1px solid #fee2e2', padding: '8px 10px', borderRadius: '6px', marginBottom: '6px', fontSize: '0.8rem', color: '#991b1b' }}>
                    <strong>⚔️ Challenge ({d.challenger}):</strong> {d.critique}
                  </div>

                  {/* Rebuttal */}
                  <div style={{ background: '#f0fdf4', border: '1px solid #dcfce7', padding: '8px 10px', borderRadius: '6px', marginBottom: '6px', fontSize: '0.8rem', color: '#166534' }}>
                    <strong>🛡️ Defense ({d.defender}):</strong> {d.rebuttal}
                  </div>

                  {/* Synthesis */}
                  <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', padding: '6px 10px', borderRadius: '6px', fontSize: '0.78rem', color: '#334155' }}>
                    <strong>⚖️ Dialectic Resolution:</strong> {d.synthesis}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Round 3: CEO Executive Synthesis */}
        {(activeTab === 'all' || activeTab === 'synthesis') && (
          <div style={{ margin: '16px 0', display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <h3 style={{ fontSize: '0.85rem', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '2px' }}>
              Round 3: CEO Orchestrator Executive Synthesis
            </h3>

            {/* Consensus Card */}
            <div
              style={{
                background: '#eff6ff',
                padding: '14px',
                borderRadius: '10px',
                border: '1px solid #bfdbfe',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}
            >
              <div>
                <span style={{ fontSize: '11px', color: '#1d4ed8', textTransform: 'uppercase', fontWeight: 700 }}>
                  CEO Executive Consensus:
                </span>
                <div style={{ color: '#1e40af', fontSize: '1.1rem', fontWeight: 800 }}>
                  {data.consensus || 'CONDITIONAL GO'}
                </div>
              </div>
              <span
                style={{
                  fontSize: '11px',
                  background: '#ffffff',
                  color: '#2563eb',
                  padding: '4px 10px',
                  borderRadius: '6px',
                  fontWeight: 600,
                  border: '1px solid #93c5fd',
                }}
              >
                Confidence: {data.confidence || 'High'}
              </span>
            </div>

            {/* Key Tradeoff */}
            {data.keyTradeoff && (
              <div
                style={{
                  background: '#fff7ed',
                  padding: '10px 14px',
                  borderRadius: '8px',
                  border: '1px solid #ffedd5',
                  color: '#c2410c',
                  fontSize: '12px',
                }}
              >
                <strong>Key Executive Tradeoff:</strong> {data.keyTradeoff}
              </div>
            )}

            {/* OMTM */}
            {data.oneMetricThatMatters && (
              <div
                style={{
                  background: '#fdf4ff',
                  padding: '10px 14px',
                  borderRadius: '8px',
                  border: '1px solid #fae8ff',
                  color: '#86198f',
                  fontSize: '12px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                }}
              >
                <Target size={15} style={{ color: '#a21caf' }} />
                <span><strong>One Metric That Matters (OMTM):</strong> {data.oneMetricThatMatters}</span>
              </div>
            )}

            {/* Recommended MVE */}
            {data.recommendedExperiment && (
              <div
                style={{
                  background: '#f0fdf4',
                  padding: '12px 14px',
                  borderRadius: '8px',
                  border: '1px solid #bbf7d0',
                  color: '#15803d',
                  fontSize: '12px',
                }}
              >
                <strong style={{ display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '2px' }}>
                  <FlaskConical size={14} /> 2-Week Minimum Viable Experiment (MVE):
                </strong>
                {data.recommendedExperiment}
              </div>
            )}

            {/* Kill Criteria */}
            {data.killCriteria && (
              <div
                style={{
                  background: '#fef2f2',
                  padding: '10px 14px',
                  borderRadius: '8px',
                  border: '1px solid #fee2e2',
                  color: '#991b1b',
                  fontSize: '12px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                }}
              >
                <Skull size={15} style={{ color: '#dc2626' }} />
                <span><strong>Kill Criteria (Rollback Trigger):</strong> {data.killCriteria}</span>
              </div>
            )}
          </div>
        )}

        {/* Footer */}
        <div className="modal-footer" style={{ marginTop: '16px' }}>
          <button className="primary-button" onClick={onClose}>
            Close Executive Debate
          </button>
        </div>
      </section>
    </div>
  )
}

