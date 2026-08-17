import React, { useState } from 'react'
import { auditMeddpiccDeal, coachSalesObjection, runPreMortemAnalysis, calculatePmfScore } from '../api'

export const ExecutiveToolsHub: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'sales' | 'tech' | 'product'>('sales')

  // CRO State
  const [metricsDefined, setMetricsDefined] = useState(true)
  const [hasEconomicBuyer, setHasEconomicBuyer] = useState(false)
  const [decisionCriteriaKnown, setDecisionCriteriaKnown] = useState(true)
  const [decisionProcessMapped, setDecisionProcessMapped] = useState(false)
  const [paperProcessMapped, setPaperProcessMapped] = useState(false)
  const [painImplicated, setPainImplicated] = useState(true)
  const [hasChampion, setHasChampion] = useState(true)
  const [competitionIdentified, setCompetitionIdentified] = useState(true)
  const [dealResult, setDealResult] = useState<any>(null)
  const [dealLoading, setDealLoading] = useState(false)

  // CTO State
  const [proposalTitle, setProposalTitle] = useState('')
  const [technicalScope, setTechnicalScope] = useState('')
  const [preMortemResult, setPreMortemResult] = useState<any>(null)
  const [techLoading, setTechLoading] = useState(false)

  // Product State
  const [veryDisappointed, setVeryDisappointed] = useState(35)
  const [somewhatDisappointed, setSomewhatDisappointed] = useState(40)
  const [notDisappointed, setNotDisappointed] = useState(25)
  const [pmfResult, setPmfResult] = useState<any>(null)

  const handleAuditDeal = async () => {
    setDealLoading(true)
    try {
      const res = await auditMeddpiccDeal({
        metricsDefined,
        hasEconomicBuyer,
        decisionCriteriaKnown,
        decisionProcessMapped,
        paperProcessMapped,
        painImplicated,
        hasChampion,
        competitionIdentified
      })
      setDealResult(res)
    } catch (err) {
      console.error(err)
    } finally {
      setDealLoading(false)
    }
  }

  const handleRunPreMortem = async () => {
    if (!proposalTitle) return
    setTechLoading(true)
    try {
      const res = await runPreMortemAnalysis({
        proposalTitle,
        technicalScope: technicalScope || 'Standard architectural implementation'
      })
      setPreMortemResult(res)
    } catch (err) {
      console.error(err)
    } finally {
      setTechLoading(false)
    }
  }

  const handleCalculatePmf = async () => {
    try {
      const res = await calculatePmfScore({
        veryDisappointedCount: veryDisappointed,
        somewhatDisappointedCount: somewhatDisappointed,
        notDisappointedCount: notDisappointed
      })
      setPmfResult(res)
    } catch (err) {
      console.error(err)
    }
  }

  return (
    <div style={{ backgroundColor: '#0d0d0d', border: '1px solid #222222', borderRadius: '8px', padding: '20px', color: '#ffffff' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #1a1a1a', paddingBottom: '12px', marginBottom: '16px' }}>
        <div>
          <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 600 }}>🏛️ Executive C-Suite Operating Hub</h3>
          <p style={{ margin: '4px 0 0', fontSize: '0.8rem', color: '#888888' }}>Specialized domain playbooks for Sales, Engineering, and Product Leadership</p>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            onClick={() => setActiveTab('sales')}
            style={{
              padding: '6px 14px',
              borderRadius: '4px',
              fontSize: '0.85rem',
              fontWeight: 600,
              backgroundColor: activeTab === 'sales' ? '#ffffff' : '#141414',
              color: activeTab === 'sales' ? '#000000' : '#888888',
              border: '1px solid #333333',
              cursor: 'pointer'
            }}
          >
            📈 CRO: MEDDPICC
          </button>
          <button
            onClick={() => setActiveTab('tech')}
            style={{
              padding: '6px 14px',
              borderRadius: '4px',
              fontSize: '0.85rem',
              fontWeight: 600,
              backgroundColor: activeTab === 'tech' ? '#ffffff' : '#141414',
              color: activeTab === 'tech' ? '#000000' : '#888888',
              border: '1px solid #333333',
              cursor: 'pointer'
            }}
          >
            💻 CTO: Pre-Mortem
          </button>
          <button
            onClick={() => setActiveTab('product')}
            style={{
              padding: '6px 14px',
              borderRadius: '4px',
              fontSize: '0.85rem',
              fontWeight: 600,
              backgroundColor: activeTab === 'product' ? '#ffffff' : '#141414',
              color: activeTab === 'product' ? '#000000' : '#888888',
              border: '1px solid #333333',
              cursor: 'pointer'
            }}
          >
            🎯 VP CS: PMF Engine
          </button>
        </div>
      </div>

      {/* CRO Tab: MEDDPICC */}
      {activeTab === 'sales' && (
        <div>
          <p style={{ fontSize: '0.85rem', color: '#aaaaaa', margin: '0 0 14px' }}>
            Audit enterprise pipeline deals across the 8 MEDDPICC dimensions to identify missing economic buyers and prevent deal stalls.
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '10px', marginBottom: '16px' }}>
            {[
              { label: 'Metrics Defined (ROI)', val: metricsDefined, setVal: setMetricsDefined },
              { label: 'Economic Buyer Engaged', val: hasEconomicBuyer, setVal: setHasEconomicBuyer },
              { label: 'Decision Criteria Known', val: decisionCriteriaKnown, setVal: setDecisionCriteriaKnown },
              { label: 'Decision Process Mapped', val: decisionProcessMapped, setVal: setDecisionProcessMapped },
              { label: 'Paper Process (Sec/Legal)', val: paperProcessMapped, setVal: setPaperProcessMapped },
              { label: 'Pain Implicated', val: painImplicated, setVal: setPainImplicated },
              { label: 'Internal Champion Active', val: hasChampion, setVal: setHasChampion },
              { label: 'Competition Identified', val: competitionIdentified, setVal: setCompetitionIdentified },
            ].map((item, idx) => (
              <label key={idx} style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.85rem', color: '#cccccc', backgroundColor: '#111111', padding: '8px 12px', borderRadius: '4px', border: '1px solid #222222', cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={item.val}
                  onChange={e => item.setVal(e.target.checked)}
                  style={{ accentColor: '#ffffff' }}
                />
                {item.label}
              </label>
            ))}
          </div>

          <button
            onClick={handleAuditDeal}
            disabled={dealLoading}
            style={{ padding: '8px 18px', backgroundColor: '#ffffff', color: '#000000', border: 'none', borderRadius: '4px', fontWeight: 600, cursor: 'pointer', marginBottom: '16px' }}
          >
            {dealLoading ? 'Auditing Deal...' : 'Run MEDDPICC Deal Health Audit'}
          </button>

          {dealResult && (
            <div style={{ backgroundColor: '#141414', border: '1px solid #282828', borderRadius: '6px', padding: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                <div style={{ fontSize: '1rem', fontWeight: 600, color: '#ffffff' }}>Health Score: {dealResult.healthScore} / 100</div>
                <div style={{ fontSize: '0.85rem', color: dealResult.healthScore >= 80 ? '#88ff88' : '#ffaa44', fontWeight: 600 }}>{dealResult.verdict}</div>
              </div>
              <div style={{ fontSize: '0.85rem', color: '#cccccc', marginBottom: '8px' }}>
                <strong>Immediate Tactical Action:</strong> {dealResult.recommendedNextAction}
              </div>
              {dealResult.identifiedGaps?.length > 0 && (
                <div style={{ marginTop: '10px' }}>
                  <div style={{ fontSize: '0.8rem', color: '#888888', textTransform: 'uppercase', marginBottom: '4px' }}>Stalling Risks</div>
                  {dealResult.identifiedGaps.map((g: any, i: number) => (
                    <div key={i} style={{ fontSize: '0.8rem', color: '#ff8888', marginBottom: '2px' }}>• {g.dimension}: {g.risk}</div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* CTO Tab: Pre-Mortem */}
      {activeTab === 'tech' && (
        <div>
          <p style={{ fontSize: '0.85rem', color: '#aaaaaa', margin: '0 0 14px' }}>
            Conduct a Gary Klein Pre-Mortem: simulate failure 6 months from now to uncover subtle operational bottlenecks before committing code.
          </p>
          <div style={{ marginBottom: '12px' }}>
            <label style={{ display: 'block', fontSize: '0.85rem', color: '#aaaaaa', marginBottom: '6px' }}>Proposed Technical Architecture / Major Release:</label>
            <input
              type="text"
              placeholder="e.g. Migrate transaction pipeline from PostgreSQL triggers to Apache Kafka"
              value={proposalTitle}
              onChange={e => setProposalTitle(e.target.value)}
              style={{ width: '100%', padding: '10px 12px', backgroundColor: '#0a0a0a', border: '1px solid #282828', borderRadius: '4px', color: '#ffffff', fontSize: '0.9rem' }}
            />
          </div>
          <div style={{ marginBottom: '14px' }}>
            <label style={{ display: 'block', fontSize: '0.85rem', color: '#aaaaaa', marginBottom: '6px' }}>Technical Scope & Context:</label>
            <textarea
              placeholder="Details on the migration plan, expected benefits, and timeline..."
              rows={2}
              value={technicalScope}
              onChange={e => setTechnicalScope(e.target.value)}
              style={{ width: '100%', padding: '10px 12px', backgroundColor: '#0a0a0a', border: '1px solid #282828', borderRadius: '4px', color: '#ffffff', fontSize: '0.85rem', fontFamily: 'inherit' }}
            />
          </div>

          <button
            onClick={handleRunPreMortem}
            disabled={techLoading || !proposalTitle}
            style={{ padding: '8px 18px', backgroundColor: '#ffffff', color: '#000000', border: 'none', borderRadius: '4px', fontWeight: 600, cursor: !proposalTitle ? 'not-allowed' : 'pointer', marginBottom: '16px' }}
          >
            {techLoading ? 'Simulating Failure Modes...' : 'Run Gary Klein Pre-Mortem'}
          </button>

          {preMortemResult && (
            <div style={{ backgroundColor: '#141414', border: '1px solid #282828', borderRadius: '6px', padding: '16px' }}>
              <div style={{ fontSize: '0.9rem', color: '#ffffff', fontWeight: 600, marginBottom: '6px' }}>
                Verdict: {preMortemResult.recommendation} ({preMortemResult.reversibilityAssessment?.decisionType})
              </div>
              <p style={{ fontSize: '0.85rem', color: '#cccccc', margin: '0 0 12px', fontStyle: 'italic' }}>
                "{preMortemResult.catastrophicFailureNarrative}"
              </p>
              <div style={{ fontSize: '0.8rem', color: '#888888', textTransform: 'uppercase', marginBottom: '6px' }}>Top Failure Modes & Safeguards</div>
              {preMortemResult.topFailureModes?.map((fm: any, idx: number) => (
                <div key={idx} style={{ backgroundColor: '#0a0a0a', padding: '10px', borderRadius: '4px', border: '1px solid #222222', marginBottom: '8px' }}>
                  <div style={{ fontWeight: 600, fontSize: '0.85rem', color: '#ffaaaa' }}>{fm.mode} ({fm.likelihood} Likelihood)</div>
                  <div style={{ fontSize: '0.8rem', color: '#aaaaaa', marginTop: '2px' }}><strong>Root Cause:</strong> {fm.rootCause}</div>
                  <div style={{ fontSize: '0.8rem', color: '#88ff88', marginTop: '2px' }}><strong>Preventative Safeguard:</strong> {fm.preventativeSafeguard}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Product Tab: PMF Engine */}
      {activeTab === 'product' && (
        <div>
          <p style={{ fontSize: '0.85rem', color: '#aaaaaa', margin: '0 0 14px' }}>
            Rahul Vohra (Superhuman) PMF Engine: "How would you feel if you could no longer use FounderOS?" (40% threshold benchmark).
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '14px', marginBottom: '16px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', color: '#aaaaaa', marginBottom: '4px' }}>Very Disappointed Count:</label>
              <input
                type="number"
                min={0}
                value={veryDisappointed}
                onChange={e => setVeryDisappointed(Number(e.target.value))}
                style={{ width: '100%', padding: '8px', backgroundColor: '#0a0a0a', border: '1px solid #282828', borderRadius: '4px', color: '#ffffff' }}
              />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', color: '#aaaaaa', marginBottom: '4px' }}>Somewhat Disappointed Count:</label>
              <input
                type="number"
                min={0}
                value={somewhatDisappointed}
                onChange={e => setSomewhatDisappointed(Number(e.target.value))}
                style={{ width: '100%', padding: '8px', backgroundColor: '#0a0a0a', border: '1px solid #282828', borderRadius: '4px', color: '#ffffff' }}
              />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', color: '#aaaaaa', marginBottom: '4px' }}>Not Disappointed Count:</label>
              <input
                type="number"
                min={0}
                value={notDisappointed}
                onChange={e => setNotDisappointed(Number(e.target.value))}
                style={{ width: '100%', padding: '8px', backgroundColor: '#0a0a0a', border: '1px solid #282828', borderRadius: '4px', color: '#ffffff' }}
              />
            </div>
          </div>

          <button
            onClick={handleCalculatePmf}
            style={{ padding: '8px 18px', backgroundColor: '#ffffff', color: '#000000', border: 'none', borderRadius: '4px', fontWeight: 600, cursor: 'pointer', marginBottom: '16px' }}
          >
            Compute Superhuman PMF Score
          </button>

          {pmfResult && (
            <div style={{ backgroundColor: '#141414', border: '1px solid #282828', borderRadius: '6px', padding: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <div style={{ fontSize: '1.1rem', fontWeight: 700, color: pmfResult.hasPmf ? '#88ff88' : '#ffaa44' }}>
                  PMF Score: {pmfResult.pmfScorePct}% (Target: 40%)
                </div>
                <div style={{ fontSize: '0.8rem', color: '#888888' }}>Total Sample: {pmfResult.totalResponses} users</div>
              </div>
              <p style={{ fontSize: '0.85rem', color: '#ffffff', margin: '0 0 10px' }}>{pmfResult.verdict}</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
