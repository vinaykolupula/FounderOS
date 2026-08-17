import React, { useState } from 'react'
import { generateInvestorUpdate, stageInvestorUpdateAction } from '../api'

interface InvestorUpdateModalProps {
  isOpen: boolean
  onClose: () => void
  onActionStaged?: () => void
}

export const InvestorUpdateModal: React.FC<InvestorUpdateModalProps> = ({ isOpen, onClose, onActionStaged }) => {
  const [loading, setLoading] = useState(false)
  const [staging, setStaging] = useState(false)
  const [updateData, setUpdateData] = useState<any>(null)
  const [customHighlight, setCustomHighlight] = useState('')
  const [customLowlight, setCustomLowlight] = useState('')
  const [customAsk, setCustomAsk] = useState('')
  const [statusNotice, setStatusNotice] = useState<string | null>(null)

  if (!isOpen) return null

  const handleGenerate = async () => {
    setLoading(true)
    setStatusNotice(null)
    try {
      const data = await generateInvestorUpdate({
        customHighlights: customHighlight ? [customHighlight] : undefined,
        customLowlights: customLowlight ? [customLowlight] : undefined,
        customAsks: customAsk ? [customAsk] : undefined
      })
      setUpdateData(data)
    } catch (err: any) {
      setStatusNotice(`Error generating update: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleStageAction = async () => {
    if (!updateData) return
    setStaging(true)
    try {
      await stageInvestorUpdateAction({
        subjectLine: updateData.subjectLine,
        fullMarkdown: updateData.fullMarkdown
      })
      setStatusNotice('✅ Investor update staged to Approval Queue for founder sign-off!')
      if (onActionStaged) onActionStaged()
    } catch (err: any) {
      setStatusNotice(`Error staging action: ${err.message}`)
    } finally {
      setStaging(false)
    }
  }

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0,0,0,0.85)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      backdropFilter: 'blur(4px)'
    }}>
      <div style={{
        backgroundColor: '#111111',
        border: '1px solid #333333',
        borderRadius: '8px',
        width: '90%',
        maxWidth: '850px',
        maxHeight: '90vh',
        overflowY: 'auto',
        color: '#ffffff',
        padding: '24px',
        boxShadow: '0 20px 40px rgba(0,0,0,0.6)'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #222222', paddingBottom: '16px', marginBottom: '20px' }}>
          <div>
            <h2 style={{ margin: 0, fontSize: '1.25rem', fontWeight: 600, letterSpacing: '-0.01em' }}>👑 Monthly Investor Update Synthesizer</h2>
            <p style={{ margin: '4px 0 0', fontSize: '0.85rem', color: '#888888' }}>Gold-standard YC / Paul Graham update letter grounded in live metrics and completed milestones.</p>
          </div>
          <button
            onClick={onClose}
            style={{ background: 'none', border: 'none', color: '#888888', fontSize: '1.25rem', cursor: 'pointer', padding: '4px 8px' }}
          >
            ✕
          </button>
        </div>

        {statusNotice && (
          <div style={{ padding: '10px 14px', borderRadius: '4px', marginBottom: '16px', backgroundColor: '#1a1a1a', border: '1px solid #333333', fontSize: '0.85rem', color: '#ffffff' }}>
            {statusNotice}
          </div>
        )}

        {!updateData ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', color: '#aaaaaa', marginBottom: '6px' }}>Key Highlight (Optional custom highlight):</label>
              <input
                type="text"
                placeholder="e.g. Closed first Fortune 500 paid pilot with $60k ACV"
                value={customHighlight}
                onChange={e => setCustomHighlight(e.target.value)}
                style={{ width: '100%', padding: '10px 12px', backgroundColor: '#0a0a0a', border: '1px solid #282828', borderRadius: '4px', color: '#ffffff', fontSize: '0.9rem' }}
              />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', color: '#aaaaaa', marginBottom: '6px' }}>Lowlight / Hard Problem (Optional):</label>
              <input
                type="text"
                placeholder="e.g. Long security review cycles delayed Q3 enterprise deployment by 3 weeks"
                value={customLowlight}
                onChange={e => setCustomLowlight(e.target.value)}
                style={{ width: '100%', padding: '10px 12px', backgroundColor: '#0a0a0a', border: '1px solid #282828', borderRadius: '4px', color: '#ffffff', fontSize: '0.9rem' }}
              />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', color: '#aaaaaa', marginBottom: '6px' }}>Specific Ask from Investors (Optional):</label>
              <input
                type="text"
                placeholder="e.g. Warm intros to VPs of Engineering at Series B SaaS companies"
                value={customAsk}
                onChange={e => setCustomAsk(e.target.value)}
                style={{ width: '100%', padding: '10px 12px', backgroundColor: '#0a0a0a', border: '1px solid #282828', borderRadius: '4px', color: '#ffffff', fontSize: '0.9rem' }}
              />
            </div>

            <div style={{ marginTop: '12px', display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
              <button
                onClick={onClose}
                style={{ padding: '8px 16px', backgroundColor: '#1a1a1a', border: '1px solid #333333', color: '#cccccc', borderRadius: '4px', cursor: 'pointer' }}
              >
                Cancel
              </button>
              <button
                onClick={handleGenerate}
                disabled={loading}
                style={{ padding: '8px 20px', backgroundColor: '#ffffff', color: '#000000', border: 'none', borderRadius: '4px', fontWeight: 600, cursor: loading ? 'not-allowed' : 'pointer' }}
              >
                {loading ? 'Synthesizing Update...' : 'Generate Investor Update'}
              </button>
            </div>
          </div>
        ) : (
          <div>
            <div style={{ backgroundColor: '#080808', border: '1px solid #222222', borderRadius: '6px', padding: '18px', marginBottom: '20px', maxHeight: '50vh', overflowY: 'auto' }}>
              <div style={{ fontSize: '0.85rem', color: '#888888', marginBottom: '12px' }}>
                <strong>Subject:</strong> {updateData.subjectLine}
              </div>
              <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace', fontSize: '0.85rem', color: '#e0e0e0', margin: 0 }}>
                {updateData.fullMarkdown}
              </pre>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <button
                onClick={() => setUpdateData(null)}
                style={{ padding: '8px 16px', backgroundColor: '#1a1a1a', border: '1px solid #333333', color: '#cccccc', borderRadius: '4px', cursor: 'pointer' }}
              >
                ← Edit Inputs
              </button>
              <div style={{ display: 'flex', gap: '12px' }}>
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(updateData.fullMarkdown)
                    setStatusNotice('📋 Copied full markdown letter to clipboard!')
                  }}
                  style={{ padding: '8px 16px', backgroundColor: '#1f1f1f', border: '1px solid #333333', color: '#ffffff', borderRadius: '4px', cursor: 'pointer' }}
                >
                  Copy Markdown
                </button>
                <button
                  onClick={handleStageAction}
                  disabled={staging}
                  style={{ padding: '8px 20px', backgroundColor: '#ffffff', color: '#000000', border: 'none', borderRadius: '4px', fontWeight: 600, cursor: staging ? 'not-allowed' : 'pointer' }}
                >
                  {staging ? 'Staging...' : 'Stage for Approval (Draft Action)'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
