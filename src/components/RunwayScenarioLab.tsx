import React, { useState, useEffect } from 'react'
import { calculateRunwayAnalysis, simulateFinancialScenario } from '../api'

interface RunwayScenarioLabProps {
  initialCash?: number
  initialBurn?: number
  initialRev?: number
}

export const RunwayScenarioLab: React.FC<RunwayScenarioLabProps> = ({
  initialCash = 500000,
  initialBurn = 35000,
  initialRev = 12000
}) => {
  const [cashBalance, setCashBalance] = useState(initialCash)
  const [monthlyBurn, setMonthlyBurn] = useState(initialBurn)
  const [monthlyRevenue, setMonthlyRevenue] = useState(initialRev)
  const [momGrowthRate, setMomGrowthRate] = useState(8) // 8% MoM

  // Scenario knobs
  const [headcountDelta, setHeadcountDelta] = useState(0)
  const [avgSalary, setAvgSalary] = useState(140000)
  const [revGrowthDeltaPct, setRevGrowthDeltaPct] = useState(0)
  const [toolingSpendDelta, setToolingSpendDelta] = useState(0)

  const [analysisResult, setAnalysisResult] = useState<any>(null)
  const [scenarioResult, setScenarioResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const fetchAnalysis = async () => {
    setLoading(true)
    try {
      if (headcountDelta === 0 && revGrowthDeltaPct === 0 && toolingSpendDelta === 0) {
        const res = await calculateRunwayAnalysis({
          cashBalance,
          monthlyBurn,
          monthlyRevenue,
          momGrowthRate: momGrowthRate / 100.0
        })
        setAnalysisResult(res)
        setScenarioResult(null)
      } else {
        const sim = await simulateFinancialScenario({
          cashBalance,
          monthlyBurn,
          monthlyRevenue,
          momGrowthRate: momGrowthRate / 100.0,
          headcountDelta,
          avgAnnualSalary: avgSalary,
          revGrowthDeltaPct,
          monthlyToolingSpendDelta: toolingSpendDelta
        })
        setAnalysisResult(sim.baseline)
        setScenarioResult(sim)
      }
    } catch (err) {
      console.error('Failed to run runway calculation:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAnalysis()
  }, [cashBalance, monthlyBurn, monthlyRevenue, momGrowthRate, headcountDelta, avgSalary, revGrowthDeltaPct, toolingSpendDelta])

  const currentDisplay = scenarioResult ? scenarioResult.scenario : analysisResult

  return (
    <div style={{ backgroundColor: '#0d0d0d', border: '1px solid #222222', borderRadius: '8px', padding: '20px', color: '#ffffff' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: '1px solid #1a1a1a', paddingBottom: '14px', marginBottom: '18px' }}>
        <div>
          <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 600 }}>💰 Default Alive Runway Lab & What-If Simulator</h3>
          <p style={{ margin: '4px 0 0', fontSize: '0.8rem', color: '#888888' }}>Paul Graham Capital Efficiency & Cash Trajectory Engine</p>
        </div>
        {currentDisplay && (
          <div style={{
            padding: '6px 14px',
            borderRadius: '4px',
            fontSize: '0.85rem',
            fontWeight: 700,
            letterSpacing: '0.04em',
            backgroundColor: currentDisplay.isDefaultAlive ? '#000000' : '#111111',
            color: currentDisplay.isDefaultAlive ? '#ffffff' : '#aaaaaa',
            border: `1px solid ${currentDisplay.isDefaultAlive ? '#ffffff' : '#444444'}`
          }}>
            {currentDisplay.status.replace('_', ' ')} • {currentDisplay.runwayMonths} MO RUNWAY
          </div>
        )}
      </div>

      {currentDisplay && (
        <div style={{ backgroundColor: '#141414', border: '1px solid #282828', borderRadius: '6px', padding: '14px', marginBottom: '20px' }}>
          <div style={{ fontSize: '0.9rem', color: '#ffffff', fontWeight: 500 }}>
            {currentDisplay.verdict}
          </div>
          {scenarioResult && (
            <div style={{ marginTop: '8px', fontSize: '0.8rem', color: scenarioResult.impact.runwayMonthsDelta >= 0 ? '#88ff88' : '#ff8888' }}>
              Scenario Impact: {scenarioResult.impact.summary} (Monthly Net Burn Δ: ${scenarioResult.impact.burnDelta.toLocaleString()})
            </div>
          )}
        </div>
      )}

      {/* Grid of Sliders */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px' }}>
        {/* Baseline Controls */}
        <div style={{ backgroundColor: '#111111', padding: '14px', borderRadius: '6px', border: '1px solid #1f1f1f' }}>
          <div style={{ fontSize: '0.8rem', fontWeight: 600, color: '#888888', textTransform: 'uppercase', marginBottom: '12px' }}>Current Baseline</div>
          
          <div style={{ marginBottom: '12px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: '#cccccc' }}>
              <span>Cash Balance:</span>
              <span style={{ fontWeight: 600, color: '#ffffff' }}>${cashBalance.toLocaleString()}</span>
            </div>
            <input
              type="range"
              min={10000}
              max={2000000}
              step={10000}
              value={cashBalance}
              onChange={e => setCashBalance(Number(e.target.value))}
              style={{ width: '100%', accentColor: '#ffffff' }}
            />
          </div>

          <div style={{ marginBottom: '12px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: '#cccccc' }}>
              <span>Monthly Gross Expenses:</span>
              <span style={{ fontWeight: 600, color: '#ffffff' }}>${monthlyBurn.toLocaleString()}</span>
            </div>
            <input
              type="range"
              min={5000}
              max={150000}
              step={2500}
              value={monthlyBurn}
              onChange={e => setMonthlyBurn(Number(e.target.value))}
              style={{ width: '100%', accentColor: '#ffffff' }}
            />
          </div>

          <div style={{ marginBottom: '12px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: '#cccccc' }}>
              <span>Monthly Revenue (MRR):</span>
              <span style={{ fontWeight: 600, color: '#ffffff' }}>${monthlyRevenue.toLocaleString()}</span>
            </div>
            <input
              type="range"
              min={0}
              max={100000}
              step={1000}
              value={monthlyRevenue}
              onChange={e => setMonthlyRevenue(Number(e.target.value))}
              style={{ width: '100%', accentColor: '#ffffff' }}
            />
          </div>

          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: '#cccccc' }}>
              <span>MoM Revenue Growth Rate:</span>
              <span style={{ fontWeight: 600, color: '#ffffff' }}>{momGrowthRate}%</span>
            </div>
            <input
              type="range"
              min={0}
              max={40}
              step={1}
              value={momGrowthRate}
              onChange={e => setMomGrowthRate(Number(e.target.value))}
              style={{ width: '100%', accentColor: '#ffffff' }}
            />
          </div>
        </div>

        {/* What-If Scenario Levers */}
        <div style={{ backgroundColor: '#111111', padding: '14px', borderRadius: '6px', border: '1px solid #1f1f1f' }}>
          <div style={{ fontSize: '0.8rem', fontWeight: 600, color: '#888888', textTransform: 'uppercase', marginBottom: '12px' }}>What-If Scenario Levers</div>

          <div style={{ marginBottom: '12px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: '#cccccc' }}>
              <span>New Hires (+/- headcount):</span>
              <span style={{ fontWeight: 600, color: '#ffffff' }}>{headcountDelta > 0 ? `+${headcountDelta}` : headcountDelta} Engineers / Reps</span>
            </div>
            <input
              type="range"
              min={-3}
              max={5}
              step={1}
              value={headcountDelta}
              onChange={e => setHeadcountDelta(Number(e.target.value))}
              style={{ width: '100%', accentColor: '#ffffff' }}
            />
          </div>

          <div style={{ marginBottom: '12px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: '#cccccc' }}>
              <span>Growth Acceleration (Δ MoM %):</span>
              <span style={{ fontWeight: 600, color: '#ffffff' }}>{revGrowthDeltaPct > 0 ? `+${revGrowthDeltaPct}` : revGrowthDeltaPct}%</span>
            </div>
            <input
              type="range"
              min={-5}
              max={15}
              step={1}
              value={revGrowthDeltaPct}
              onChange={e => setRevGrowthDeltaPct(Number(e.target.value))}
              style={{ width: '100%', accentColor: '#ffffff' }}
            />
          </div>

          <div style={{ marginBottom: '12px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: '#cccccc' }}>
              <span>SaaS / Infra Tooling Spend (Δ $/mo):</span>
              <span style={{ fontWeight: 600, color: '#ffffff' }}>${toolingSpendDelta.toLocaleString()}</span>
            </div>
            <input
              type="range"
              min={-2000}
              max={10000}
              step={500}
              value={toolingSpendDelta}
              onChange={e => setToolingSpendDelta(Number(e.target.value))}
              style={{ width: '100%', accentColor: '#ffffff' }}
            />
          </div>

          <button
            onClick={() => {
              setHeadcountDelta(0)
              setRevGrowthDeltaPct(0)
              setToolingSpendDelta(0)
            }}
            style={{
              padding: '6px 12px',
              backgroundColor: '#1a1a1a',
              border: '1px solid #333333',
              color: '#aaaaaa',
              borderRadius: '4px',
              fontSize: '0.8rem',
              cursor: 'pointer'
            }}
          >
            ↺ Reset Scenario Levers
          </button>
        </div>
      </div>
    </div>
  )
}
