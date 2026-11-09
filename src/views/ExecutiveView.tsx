import { type CompanyProfile } from '../domain'
import { RunwayScenarioLab } from '../components/RunwayScenarioLab'
import { ExecutiveToolsHub } from '../components/ExecutiveToolsHub'

export function ExecutiveView({
  company: _company,
  onOpenInvestorModal,
}: {
  company: CompanyProfile
  onOpenInvestorModal: () => void
}) {
  return (
    <div className="page simple-page">
      <div className="simple-heading">
        <div>
          <p className="eyebrow">C-SUITE OPERATING COCKPIT</p>
          <h1>Executive Daily Operating Tools</h1>
          <p className="subhead">
            Framework-driven tools for CEO Investor updates, CFO Runway simulations, CRO MEDDPICC audits, CTO Pre-Mortems, and Product PMF.
          </p>
        </div>
        <div>
          <button className="primary-button" onClick={onOpenInvestorModal}>
            👑 Monthly Investor Update
          </button>
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', marginTop: '16px' }}>
        <RunwayScenarioLab initialCash={450000} initialBurn={28000} initialRev={12000} />
        <ExecutiveToolsHub />
      </div>
    </div>
  )
}

