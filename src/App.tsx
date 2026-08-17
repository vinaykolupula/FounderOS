/**
 * FounderOS Main Application Shell & Executive Command Center
 * 
 * Main UI Router and Controller handling:
 * 1. Setup & Onboarding Wizard (Company stage, Founder DNA, Architecture, Connectors).
 * 2. Real-time WebSocket connection to backend event manager.
 * 3. Navigation Views (Overview, Tasks, Decisions Ledger, CEO Intelligence, Company Architecture, Connections, AI Models Settings).
 * 4. Modal Dialogs (Multi-Agent Executive Debate, Task Delegation, Decision Creation, Profile Editors).
 * 5. Global Error & Success Notification Toast system.
 */

import { useEffect, useState } from 'react'
import {
  createBackendTask, delegateBackendTask, fetchBackendTasks, scanAgentTasks, updateBackendTask,
  approveBackendAction, configureBackendConnector, createBackendDecision, fetchBackendWorkspace, fetchGoogleAuthUrl, fetchModelSettings, saveModelSetting, submitBackendOnboarding, testModelConnection, triggerExecutiveDebate, updateBackendCompany, updateBackendFounder, resetBackendWorkspace, fetchMorningBriefing,
  discoverProviderModels
} from './api'
import {
  ArrowUpRight, Bell, BookOpenCheck, Bot, Calendar, Check, CheckCircle2, CheckSquare, ChevronRight, CircleAlert,
  CircleDot, Clock, Command, Compass, Cpu, Database, Eye, EyeOff, FileText, Flame, FlaskConical, Gauge, LayoutDashboard, LineChart,
  ListChecks, ListTodo, Mail, Menu, MoreHorizontal, Plus, Plug, RefreshCw, Search, Settings,
  ShieldCheck, Sparkles, X, Send, Sun
} from 'lucide-react'
import { createWorkspace, defaultCompany, defaultFounder, type CompanyProfile, type FounderProfile, type Connector, type ConnectorId, type TaskItem, type View, type Workspace } from './domain'
import { usePersistentState } from './usePersistentState'
import { InvestorUpdateModal } from './components/InvestorUpdateModal'
import { RunwayScenarioLab } from './components/RunwayScenarioLab'
import { ExecutiveToolsHub } from './components/ExecutiveToolsHub'

const nav: { label: View; icon: typeof LayoutDashboard }[] = [
  { label: 'Overview', icon: LayoutDashboard },
  { label: 'Tasks', icon: ListTodo },
  { label: 'Executive', icon: LineChart },
  { label: 'Decisions', icon: BookOpenCheck },
  { label: 'Intelligence', icon: Compass },
  { label: 'Company', icon: Gauge },
  { label: 'Connections', icon: Plug },
  { label: 'Models', icon: Cpu },
]

const signals: any[] = []

function App() {
  const [workspace, setWorkspace] = usePersistentState<Workspace>('founderos-workspace-v1', createWorkspace())
  const [view, setView] = useState<View>('Overview')
  const [drawerOpen, setDrawerOpen] = useState(false)
  const [briefUpdated, setBriefUpdated] = useState(false)
  const [notice, setNotice] = useState('')
  const [errorNotice, setErrorNotice] = useState('')
  const [companyEditorOpen, setCompanyEditorOpen] = useState(false)
  const [founderEditorOpen, setFounderEditorOpen] = useState(false)
  const [debateModal, setDebateModal] = useState<any>(null)
  const [newDecisionOpen, setNewDecisionOpen] = useState(false)
  const [newTaskOpen, setNewTaskOpen] = useState(false)
  const [investorModalOpen, setInvestorModalOpen] = useState(false)
  const [tasksList, setTasksList] = useState<any[]>([])

  // Interactive Modal States
  const [askModalOpen, setAskModalOpen] = useState(false)
  const [previewAction, setPreviewAction] = useState<any>(null)
  const [activeSignal, setActiveSignal] = useState<any>(null)
  const [notificationsOpen, setNotificationsOpen] = useState(false)
  const [briefingModalOpen, setBriefingModalOpen] = useState(false)
  const [briefingData, setBriefingData] = useState<any>(null)

  const navigate = (target: View) => {
    setView(target)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const refreshTasks = () => {
    fetchBackendTasks().then((res) => {
      if (Array.isArray(res)) {
        setTasksList(res)
      }
    }).catch(() => {})
  }

  useEffect(() => {
    fetchBackendWorkspace().then((remoteWs) => {
      if (remoteWs) {
        setWorkspace(remoteWs)
      }
    })
    refreshTasks()
  }, [])

  useEffect(() => {
    if (!workspace?.id) return

    let isSubscribed = true
    let reconnectTimeout: any = null
    let ws: WebSocket | null = null

    const connectWebSocket = () => {
      if (!isSubscribed) return
      try {
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
        const wsHost = (import.meta as any).env?.VITE_WS_HOST || '127.0.0.1:8000'
        const wsUrl = `${wsProtocol}//${wsHost}/ws/${workspace.id}`
        ws = new WebSocket(wsUrl)

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data)
            if (data.type === 'REFRESH') {
              fetchBackendWorkspace().then((remoteWs) => remoteWs && setWorkspace(remoteWs))
              refreshTasks()
              setNotice('System state updated in background.')
            }
          } catch (e) {
            // ignore
          }
        }

        ws.onclose = () => {
          if (isSubscribed) {
            reconnectTimeout = setTimeout(connectWebSocket, 3000)
          }
        }

        ws.onerror = () => {
          ws?.close()
        }
      } catch (err) {
        if (isSubscribed) {
          reconnectTimeout = setTimeout(connectWebSocket, 3000)
        }
      }
    }

    connectWebSocket()

    return () => {
      isSubscribed = false
      if (reconnectTimeout) clearTimeout(reconnectTimeout)
      if (ws) ws.close()
    }
  }, [workspace?.id])

  const handleScanTasks = async () => {
    try {
      setNotice('Agent scanning connected platforms (Gmail, Calendar, Linear)...')
      const res = await scanAgentTasks()
      if (res && res.length > 0) {
        setTasksList(res)
        setNotice('Agent scan complete! Discovered and prioritized founder tasks.')
      }
    } catch (e: any) {
      setErrorNotice(e.message || 'Failed to scan tasks')
    }
  }

  const handleDelegateTask = async (id: number) => {
    try {
      await delegateBackendTask(id)
      refreshTasks()
      setNotice('Task delegated to FounderOS Agent for autonomous processing.')
    } catch (e: any) {
      setErrorNotice(e.message || 'Failed to delegate task')
    }
  }

  const handleCompleteTask = async (id: number) => {
    try {
      await updateBackendTask(id, { status: 'COMPLETED' })
      refreshTasks()
      setNotice('Task marked as completed.')
    } catch (e: any) {
      setErrorNotice(e.message || 'Failed to complete task')
    }
  }

  const updateWorkspace = (update: Partial<Workspace>) => setWorkspace((current) => ({ ...current, ...update }))
  const updateCompany = async (company: CompanyProfile) => {
    try {
      updateWorkspace({ company })
      await updateBackendCompany(company)
      setCompanyEditorOpen(false)
      setNotice('Company model updated. Future briefs will use this context.')
    } catch (e: any) {
      setErrorNotice(e.message || 'Failed to update company')
    }
  }
  const updateFounder = async (founder: FounderProfile) => {
    try {
      updateWorkspace({ founder })
      await updateBackendFounder(founder)
      setFounderEditorOpen(false)
      setNotice('Founder profile updated.')
    } catch (e: any) {
      setErrorNotice(e.message || 'Failed to update founder')
    }
  }
  const approveAction = async (id: number) => {
    try {
      const item = (workspace?.actions || []).find((action) => action.id === id)
      updateWorkspace({ actions: (workspace?.actions || []).filter((action) => action.id !== id) })
      await approveBackendAction(id)
      setNotice(`${item?.title || 'Action'} approved and dispatched. Execution receipt saved.`)
    } catch (e: any) {
      setErrorNotice(e.message || 'Failed to approve action')
    }
  }
  const refreshBrief = async () => {
    setBriefUpdated(true)
    try {
      const briefing = await fetchMorningBriefing()
      if (briefing) {
        setBriefingData(briefing)
        setBriefingModalOpen(true)
      }
      const remoteWs = await fetchBackendWorkspace()
      if (remoteWs) setWorkspace(remoteWs)
      setNotice('CEO Morning Briefing synthesized from overnight signals.')
    } catch (e: any) {
      setErrorNotice(e.message || 'Failed to assemble morning briefing')
    } finally {
      window.setTimeout(() => setBriefUpdated(false), 800)
    }
  }
  const configureConnector = async (id: ConnectorId) => {
    try {
      const connector = (workspace?.connectors || []).find((item) => item.id === id)
      updateWorkspace({ connectors: (workspace?.connectors || []).map((item) => item.id === id ? { ...item, status: 'configured' as const } : item) })
      await configureBackendConnector(id)

      if (id === 'gmail') {
        const authUrl = await fetchGoogleAuthUrl()
        if (authUrl) {
          setNotice('Google Workspace connection authorized. Tokens encrypted in Vault.')
        } else {
          setNotice('Google Workspace setup saved.')
        }
      } else {
        setNotice(`${connector?.name} setup saved. OAuth credentials recorded.`)
      }
    } catch (e: any) {
      setErrorNotice(e.message || 'Failed to configure connector')
    }
  }

  const handleResetWorkspace = async () => {
    if (window.confirm("Are you sure you want to reset everything? This will delete all company data, founder profile, and agent history.")) {
      try {
        const ok = await resetBackendWorkspace()
        if (ok) {
          setWorkspace(createWorkspace())
          setNotice('Workspace has been completely reset.')
        } else {
          setErrorNotice('Failed to reset workspace.')
        }
      } catch (e: any) {
        setErrorNotice(e.message || 'Failed to reset workspace.')
      }
    }
  }

  const safeWorkspace = workspace || createWorkspace()
  const safeCompany = safeWorkspace.company || defaultCompany
  const safeFounder = safeWorkspace.founder || defaultFounder
  const safeConnectors = safeWorkspace.connectors || []
  const safeActions = safeWorkspace.actions || []
  const safeDecisions = safeWorkspace.decisions || []

  const companyName = safeCompany.name || 'FounderOS'
  const founderName = safeFounder.name || 'Vishwa'

  if (!safeWorkspace.isOnboarded) {
    return <Onboarding onComplete={(company, founder, selectedConnectors) => {
      const updatedWs: Workspace = { ...createWorkspace(), isOnboarded: true, company, founder, connectors: createWorkspace().connectors.map((connector) => ({ ...connector, status: selectedConnectors.includes(connector.id) ? 'configured' : 'not_connected' })) }
      setWorkspace(updatedWs)
      submitBackendOnboarding(company, founder, selectedConnectors)
    }} />
  }

  return <main className="app-shell">
    <aside className={`sidebar ${drawerOpen ? 'is-open' : ''}`}>
      <div className="brand-row"><img src="/media/Logo.webp" alt="FounderOS Logo" className="brand-logo-img" /><span>FounderOS</span><button className="mobile-close" onClick={() => setDrawerOpen(false)} aria-label="Close navigation"><X size={18} /></button></div>
      <div className="workspace-switcher"><div className="workspace-orb">{companyName.charAt(0).toUpperCase()}</div><div><strong>{companyName}</strong><small>Founder workspace</small></div><ChevronRight size={16} /></div>
      <nav><p className="nav-label">WORKSPACE</p>{nav.map(({ label, icon: Icon }) => <button key={label} className={`nav-item ${view === label ? 'active' : ''}`} onClick={() => { navigate(label); setDrawerOpen(false) }}><Icon size={17} /><span>{label}</span>{label === 'Decisions' && <em>{safeDecisions.length || 3}</em>}{label === 'Connections' && safeConnectors.some((connector) => connector.status === 'configured') && <i className="nav-ready" />}</button>)}</nav>
      <div className="sidebar-bottom"><button className="nav-item" onClick={() => navigate('Models')}><Settings size={17} /><span>Settings</span></button><div className="profile" onClick={() => setFounderEditorOpen(true)} style={{ cursor: 'pointer' }}><div className="avatar">{founderName.slice(0, 2).toUpperCase()}</div><div><strong>{founderName}</strong><small>{safeFounder.role}</small></div><MoreHorizontal size={17} /></div></div>
    </aside>
    {drawerOpen && <button className="scrim" onClick={() => setDrawerOpen(false)} aria-label="Close navigation" />}
    <section className="content">
      <header className="topbar">
        <button className="menu-button" onClick={() => setDrawerOpen(true)} aria-label="Open navigation"><Menu size={21} /></button>
        <div className="crumb"><span>Workspace</span><ChevronRight size={14} /><strong>{view}</strong></div>
        <div className="topbar-actions">
          <button className="icon-button" onClick={() => setAskModalOpen(true)} title="Search"><Search size={18} /></button>
          <button className="icon-button notification" onClick={() => setNotificationsOpen(!notificationsOpen)} title="Notifications"><Bell size={18} /><i /></button>
          <button className="ask-button" onClick={() => setAskModalOpen(true)}><Command size={15} /> Ask FounderOS</button>
        </div>
      </header>

      {notice && <div className="toast"><Check size={15} />{notice}<button onClick={() => setNotice('')}><X size={14} /></button></div>}
      {errorNotice && <div className="toast error-toast" style={{background: '#fee2e2', color: '#991b1b', border: '1px solid #ef4444'}}><CircleAlert size={15} />{errorNotice}<button style={{color: '#991b1b'}} onClick={() => setErrorNotice('')}><X size={14} /></button></div>}
      
      {notificationsOpen && <NotificationsDropdown onClose={() => setNotificationsOpen(false)} />}

      {view === 'Overview' && <Overview
        company={safeCompany}
        founder={safeFounder}
        actions={safeActions}
        onApprove={approveAction}
        onPreview={(action) => setPreviewAction(action)}
        onReviewSignal={(signal) => setActiveSignal(signal)}
        onRefresh={refreshBrief}
        briefUpdated={briefUpdated}
        onViewIntelligence={() => navigate('Intelligence')}
        onDebate={() => {
          triggerExecutiveDebate("Pause Feature B and investigate activation").then((data) => setDebateModal(data))
        }}
        onInvestorUpdate={() => setInvestorModalOpen(true)}
      />}
      
      {view === 'Tasks' && <TasksView
        tasks={tasksList}
        onScan={handleScanTasks}
        onNewTask={() => setNewTaskOpen(true)}
        onDelegate={handleDelegateTask}
        onComplete={handleCompleteTask}
      />}

      {view === 'Executive' && <ExecutiveView
        company={safeCompany}
        onOpenInvestorModal={() => setInvestorModalOpen(true)}
      />}

      {view === 'Decisions' && <Decisions
        decisions={safeDecisions}
        onOpenDebate={(title) => {
          triggerExecutiveDebate(title).then((data) => setDebateModal(data))
        }}
        onNewDecision={() => setNewDecisionOpen(true)}
      />}
      
      {view === 'Intelligence' && <Intelligence onSelectSignal={(s) => setActiveSignal(s)} />}
      
      {view === 'Company' && <Company
        company={safeCompany}
        connectedCount={safeConnectors.filter((connector) => connector.status === 'configured').length}
        onEdit={() => setCompanyEditorOpen(true)}
        onConnections={() => navigate('Connections')}
      />}
      
      {view === 'Connections' && <Connections connectors={safeConnectors} onConfigure={configureConnector} />}
      
      {view === 'Models' && <ModelsView onNotice={(msg) => setNotice(msg)} onReset={handleResetWorkspace} />}
    </section>

    {companyEditorOpen && <CompanyEditor company={safeCompany} onClose={() => setCompanyEditorOpen(false)} onSave={updateCompany} />}
    {founderEditorOpen && <FounderEditor founder={safeFounder} onClose={() => setFounderEditorOpen(false)} onSave={updateFounder} />}
    {debateModal && <DebateModal data={debateModal} onClose={() => setDebateModal(null)} />}
    {investorModalOpen && <InvestorUpdateModal isOpen={investorModalOpen} onClose={() => setInvestorModalOpen(false)} onActionStaged={() => {
      fetchBackendWorkspace().then((ws) => ws && setWorkspace(ws))
      setNotice('Investor update staged to Approval Queue for founder sign-off.')
    }} />}
    {newDecisionOpen && <NewDecisionModal onClose={() => setNewDecisionOpen(false)} onSave={async (title, detail) => {
      try {
        await createBackendDecision(title, detail)
        setNewDecisionOpen(false)
        setNotice(`Decision '${title}' added to institutional memory.`)
        const remoteWs = await fetchBackendWorkspace()
        if (remoteWs) setWorkspace(remoteWs)
      } catch (e: any) {
        setErrorNotice(e.message || 'Failed to create decision')
      }
    }} />}
    {newTaskOpen && <NewTaskModal onClose={() => setNewTaskOpen(false)} onSave={async (task) => {
      await createBackendTask(task)
      setNewTaskOpen(false)
      refreshTasks()
      setNotice(`Task '${task.title}' added to Founder Work Plan.`)
    }} />}
    {askModalOpen && <AskFounderOSModal onClose={() => setAskModalOpen(false)} onDebate={(title) => {
      setAskModalOpen(false)
      triggerExecutiveDebate(title).then((data) => setDebateModal(data))
    }} />}
    {previewAction && <PreviewActionModal action={previewAction} onClose={() => setPreviewAction(null)} onApprove={(id) => {
      approveAction(id)
      setPreviewAction(null)
    }} />}
    {activeSignal && <SignalModal signal={activeSignal} onClose={() => setActiveSignal(null)} onDebate={(title) => {
      setActiveSignal(null)
      triggerExecutiveDebate(title).then((data) => setDebateModal(data))
    }} />}
    {briefingModalOpen && <MorningBriefingModal data={briefingData} onClose={() => setBriefingModalOpen(false)} onDebate={(title) => {
      setBriefingModalOpen(false)
      triggerExecutiveDebate(title).then((data) => setDebateModal(data))
    }} />}
  </main>
}

function ExecutiveView({ company, onOpenInvestorModal }: { company: CompanyProfile; onOpenInvestorModal: () => void }) {
  return <div className="page simple-page">
    <div className="simple-heading">
      <div>
        <p className="eyebrow">C-SUITE OPERATING COCKPIT</p>
        <h1>Executive Daily Operating Tools</h1>
        <p className="subhead">Framework-driven tools for CEO Investor updates, CFO Runway simulations, CRO MEDDPICC audits, CTO Pre-Mortems, and Product PMF.</p>
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
}

function Onboarding({ onComplete }: { onComplete: (company: CompanyProfile, founder: FounderProfile, selected: ConnectorId[]) => void }) {
  const [step, setStep] = useState(1)
  const [company, setCompany] = useState(defaultCompany)
  const [founder, setFounder] = useState(defaultFounder)
  const [selected, setSelected] = useState<ConnectorId[]>([])
  const updateCompany = (field: keyof CompanyProfile, value: any) => setCompany((current) => ({ ...current, [field]: value }))
  const updateFounder = (field: keyof FounderProfile, value: any) => setFounder((current) => ({ ...current, [field]: value }))
  const toggle = (id: ConnectorId) => setSelected((current) => current.includes(id) ? current.filter((item) => item !== id) : [...current, id])
  
  const businessModels = ['B2B SaaS', 'B2C / D2C', 'Marketplace', 'Agency / Services', 'Hardware / Manufacturing', 'Open Source', 'Other']
  const platformFocuses = ['Web Application', 'Mobile App', 'API / Developer Tools', 'Chrome Extension', 'Offline / Retail', 'Other']
  const fundingStates = ['Bootstrapped', 'Pre-Seed', 'Seed', 'Series A', 'Series B+', 'Public']
  const revenueRanges = ['Pre-revenue', '<$10k MRR', '$10k-$100k MRR', '$1M+ ARR']
  const stages = ['Idea stage', 'Pre-revenue', 'Early revenue', 'Growth stage', 'Scale']
  const teamSizes = ['Solo founder', '2-5 people', '6-15 people', '16-50 people', '50+ people']
  
  const founderRoles = ['Solo Founder', 'CEO', 'CTO', 'COO', 'Other']
  const founderBackgrounds = ['Engineering / Technical', 'Product / Design', 'Sales / Go-to-Market', 'Operations / Finance', 'Marketing / Growth']
  const experienceLevels = ['First-time Founder', 'Second-time Founder', 'Serial Founder (3+)', 'Industry Veteran (10+ yrs)']
  const founderSuperpowers = ['Building & Engineering', 'Sales & Closing Deals', 'Product Vision & UX', 'Fundraising & Capital', 'Recruiting & Team Building']

  return <main className="onboarding-shell">
    <section className="onboarding-panel">
      <div className="onboarding-brand"><img src="/media/Logo.webp" alt="FounderOS Logo" className="brand-logo-img" />FounderOS</div>
      <div className="stepper">
        <span className={step >= 1 ? 'current' : ''}>01</span><i />
        <span className={step >= 2 ? 'current' : ''}>02</span><i />
        <span className={step >= 3 ? 'current' : ''}>03</span><i />
        <span className={step >= 4 ? 'current' : ''}>04</span><i />
        <span className={step >= 5 ? 'current' : ''}>05</span>
      </div>
      {step === 1 && <>
        <p className="eyebrow">IDENTITY & DIGITAL FOOTPRINT</p>
        <h1>Start with the company FounderOS should understand.</h1>
        <p className="onboarding-copy">This context gives the agent a foundation to search and scrape intelligently.</p>
        <div className="form-grid">
          <Field label="Company name" value={company.name} onChange={(value) => updateCompany('name', value)} />
          <Field label="Website URL (e.g. https://...)" value={company.websiteUrl || ''} onChange={(value) => updateCompany('websiteUrl', value)} />
          <Field label="LinkedIn Profile" value={company.linkedinUrl || ''} onChange={(value) => updateCompany('linkedinUrl', value)} />
          <Field label="Social / Twitter" value={company.socialUrl || ''} onChange={(value) => updateCompany('socialUrl', value)} />
        </div>
      </>}
      {step === 2 && <>
        <p className="eyebrow">FOUNDER DNA</p>
        <h1>Who is building {company.name || 'this'}?</h1>
        <p className="onboarding-copy">Your strengths and gaps define where the AI should actively lean in vs stay back.</p>
        <div className="form-grid">
          <Field label="Your name" value={founder.name} onChange={(value) => updateFounder('name', value)} />
          <SelectField label="Role" value={founder.role} options={founderRoles} onChange={(value) => updateFounder('role', value)} />
          <SelectField label="Core Background" value={founder.background} options={founderBackgrounds} onChange={(value) => updateFounder('background', value)} />
          <SelectField label="Experience Level" value={founder.experienceLevel} options={experienceLevels} onChange={(value) => updateFounder('experienceLevel', value)} />
          <Field label="Domain Expertise" value={founder.domainExpertise} onChange={(value) => updateFounder('domainExpertise', value)} />
          <SelectField label="Your Superpower (Strongest skill)" value={founder.superpower} options={founderSuperpowers} onChange={(value) => updateFounder('superpower', value)} />
          <SelectField label="Your Primary Gap (Weakest skill)" value={founder.primaryGap} options={founderSuperpowers} onChange={(value) => updateFounder('primaryGap', value)} />
          <Field label="Current Learning Focus" value={founder.learningFocus} onChange={(value) => updateFounder('learningFocus', value)} />
          <Field label="Communication Style (e.g. Direct, Brief)" value={founder.communicationStyle || ''} onChange={(value) => updateFounder('communicationStyle', value)} />
          <Field label="Energy State (e.g. Sprinting, Burned out)" value={founder.energyState || ''} onChange={(value) => updateFounder('energyState', value)} />
          <Field label="Core Values (e.g. Speed, Quality)" value={founder.coreValues || ''} onChange={(value) => updateFounder('coreValues', value)} />
        </div>
      </>}
      {step === 3 && <>
        <p className="eyebrow">ARCHITECTURE & SCALE</p>
        <h1>How does {company.name || 'the company'} operate?</h1>
        <p className="onboarding-copy">This architecture helps the agent calibrate its growth and execution advice.</p>
        <div className="form-grid">
          <SelectField label="Business Model" value={company.businessModel || ''} options={businessModels} onChange={(value) => updateCompany('businessModel', value)} />
          <SelectField label="Platform Focus" value={company.platformFocus || ''} options={platformFocuses} onChange={(value) => updateCompany('platformFocus', value)} />
          <SelectField label="Funding State" value={company.fundingState || ''} options={fundingStates} onChange={(value) => updateCompany('fundingState', value)} />
          <SelectField label="Revenue Range" value={company.revenueRange || ''} options={revenueRanges} onChange={(value) => updateCompany('revenueRange', value)} />
          <SelectField label="Company stage" value={company.stage} options={stages} onChange={(value) => updateCompany('stage', value)} />
          <SelectField label="Team size" value={company.teamSize} options={teamSizes} onChange={(value) => updateCompany('teamSize', value)} />
          <Field label="GTM Motion (e.g. PLG, Sales-led)" value={company.gtmMotion || ''} onChange={(value) => updateCompany('gtmMotion', value)} />
          <Field label="Burn Rate (e.g. $50k/mo)" value={company.burnRate || ''} onChange={(value) => updateCompany('burnRate', value)} />
        </div>
      </>}
      {step === 4 && <>
        <p className="eyebrow">STRATEGIC COMPASS</p>
        <h1>What are you trying to make true?</h1>
        <p className="onboarding-copy">FounderOS uses these objectives and constraints to rank what matters.</p>
        <div className="form-grid single">
          <Field label="Current objective" value={company.objective} onChange={(value) => updateCompany('objective', value)} />
          <Field label="Ideal customer" value={company.idealCustomer} onChange={(value) => updateCompany('idealCustomer', value)} />
          <Field label="Primary Metric" value={company.primaryMetric} onChange={(value) => updateCompany('primaryMetric', value)} />
          <Field label="Primary constraint right now" value={company.primaryConstraint} onChange={(value) => updateCompany('primaryConstraint', value)} />
          <NumberField label="Minimum runway (months)" value={company.runwayMonths} onChange={(value) => updateCompany('runwayMonths', value)} />
          <Field label="Tech Stack" value={company.techStack || ''} onChange={(value) => updateCompany('techStack', value)} />
          <Field label="Competitive Moat" value={company.competitiveMoat || ''} onChange={(value) => updateCompany('competitiveMoat', value)} />
        </div>
      </>}
      {step === 5 && <>
        <p className="eyebrow">SIGNAL SOURCES</p>
        <h1>Choose the first systems to connect.</h1>
        <p className="onboarding-copy">We will create secure connection setup for your selected sources. No information leaves your workspace until you complete OAuth.</p>
        <div className="source-picker">
          {(['gmail', 'slack', 'linear', 'hubspot', 'stripe'] as ConnectorId[]).map((id) => <button className={`source-option ${selected.includes(id) ? 'selected' : ''}`} onClick={() => toggle(id)} key={id}><span className="pick-icon">{selected.includes(id) ? <Check size={15} /> : <Plus size={15} />}</span><span><strong>{id === 'gmail' ? 'Google Workspace' : id[0].toUpperCase() + id.slice(1)}</strong><small>{id === 'gmail' ? 'Email and calendar' : id === 'linear' ? 'Product execution' : id === 'hubspot' ? 'Pipeline and customer data' : id === 'stripe' ? 'Revenue and subscriptions' : 'Team context and decisions'}</small></span></button>)}
        </div>
      </>}
      <div className="onboarding-footer">
        <button className="back-step" onClick={() => setStep((current) => Math.max(1, current - 1))} disabled={step === 1}>Back</button>
        {step < 5 ? <button className="primary-button wide" onClick={() => setStep((current) => current + 1)}>Continue <ChevronRight size={16} /></button> : <button className="primary-button wide" onClick={() => onComplete(company, founder, selected)}>Open command center <ArrowUpRight size={16} /></button>}
      </div>
    </section>
    <aside className="onboarding-aside">
      <div className="aside-pill"><Sparkles size={14} /> BUILT FOR FOUNDER JUDGMENT</div>
      <blockquote>“An always-on founder intelligence system.”</blockquote>
      <div className="aside-rule" />
      <p>It deeply understands your company constraints, monitors real-time signals, and automates high-leverage execution—always keeping you in the driver's seat.</p>
    </aside>
  </main>
}

function Overview({
  company,
  founder,
  actions,
  onApprove,
  onPreview,
  onReviewSignal,
  onRefresh,
  briefUpdated,
  onViewIntelligence,
  onDebate,
  onInvestorUpdate
}: {
  company: CompanyProfile;
  founder: FounderProfile;
  actions: Workspace['actions'];
  onApprove: (id: number) => void;
  onPreview: (action: any) => void;
  onReviewSignal: (signal: any) => void;
  onRefresh: () => void;
  briefUpdated: boolean;
  onViewIntelligence: () => void;
  onDebate: () => void;
  onInvestorUpdate: () => void;
}) {
  return <div className="page overview-page">
    <section className="welcome-row">
      <div>
        <p className="eyebrow">THURSDAY, AUGUST 7</p>
        <h1>Good morning, {founder.name || 'Founder'}.</h1>
        <p className="subhead">Here is what deserves your attention before you start your day.</p>
      </div>
      <div style={{ display: 'flex', gap: '8px' }}>
        <button className="secondary-button" onClick={onInvestorUpdate} style={{ height: '38px', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '6px' }}>
          👑 Investor Update
        </button>
        <button className={`refresh-button ${briefUpdated ? 'spinning' : ''}`} onClick={onRefresh}>
          <RefreshCw size={16} /> Refresh brief
        </button>
      </div>
    </section>

    <section className="health-strip">
      <div className="health-main">
        <div className="pulse-ring"><span>82</span></div>
        <div>
          <p>COMPANY HEALTH</p>
          <strong>Focused, with one emerging risk</strong>
          <small><span className="up">↗ 4 pts</span> from last week</small>
        </div>
      </div>
      <div className="health-divider" />
      <div className="health-stat">
        <span>Runway</span>
        <strong>{company.runwayMonths || 12} <small>mo</small></strong>
        <i className="stable">On plan</i>
      </div>
      <div className="health-stat">
        <span>Critical alerts</span>
        <strong>02</strong>
        <i className="attention">Needs attention</i>
      </div>
      <div className="health-stat">
        <span>Momentum</span>
        <strong>Rising</strong>
        <i className="stable">+18% pipeline</i>
      </div>
    </section>

    <section className="grid-main">
      <article className="card recommendation-card">
        <div className="card-topline">
          <span className="section-kicker"><Sparkles size={14} /> CEO RECOMMENDATION</span>
          <button className="quiet-button" onClick={onDebate}>Executive Debate <ArrowUpRight size={14} /></button>
        </div>
        <div className="recommendation-content">
          <div className="recommendation-number">01</div>
          <div>
            <h2>Pause Feature B. Fix activation first.</h2>
            <p>Experiment B correlates with a 12% fall in {company.primaryConstraint || 'first-value completion'}. This is now the clearest constraint on new revenue.</p>
          </div>
        </div>
        <div className="evidence-grid">
          <div><span>Evidence</span><strong>3 independent signals</strong></div>
          <div><span>Confidence</span><strong>High evidence</strong></div>
          <div><span>Decision review</span><strong>Friday, 3:30 PM</strong></div>
        </div>
        <div className="counterpoint">
          <CircleAlert size={16} />
          <span><strong>Skeptic view:</strong> The decline could be seasonal. Use five customer interviews to rule this out.</span>
        </div>
      </article>

      <aside className="card focus-card">
        <div className="card-topline">
          <span className="section-kicker"><ListChecks size={14} /> TODAY'S FOCUS</span>
          <span className="count-pill">3 items</span>
        </div>
        <div className="focus-list">
          <div onClick={onDebate} style={{ cursor: 'pointer' }}><Focus index="1" title="Approve activation investigation" detail="Unblocks Product and Engineering" /></div>
          <div onClick={() => onViewIntelligence()} style={{ cursor: 'pointer' }}><Focus index="2" title="Join enterprise discovery call" detail="2:00 PM · Atlas Logistics" /></div>
          <div onClick={onDebate} style={{ cursor: 'pointer' }}><Focus index="3" title="Review hiring plan" detail="Draft needs your judgment" /></div>
        </div>
      </aside>
    </section>

    <section className="section-header">
      <div>
        <h2>What changed</h2>
        <p>Signals ranked by potential impact on your goals.</p>
      </div>
      <button className="text-button" onClick={onViewIntelligence}>View intelligence <ChevronRight size={16} /></button>
    </section>

    <section className="signal-grid">
      {signals.map((signal) => <article className={`signal-card ${signal.tone}`} key={signal.title}>
        <div className="signal-top">
          <span>{signal.tag}</span>
          <MoreHorizontal size={17} />
        </div>
        <h3>{signal.title}</h3>
        <p>{signal.body}</p>
        <button onClick={() => onReviewSignal(signal)}>Review signal <ArrowUpRight size={14} /></button>
      </article>)}
    </section>

    <section className="section-header action-header">
      <div>
        <h2>Ready for your approval</h2>
        <p>FounderOS prepares work. You keep final control.</p>
      </div>
      <span className="approval-note"><ShieldCheck size={15} /> Approval required</span>
    </section>

    <section className="approval-list">
      {actions.length === 0 ? <div className="empty-state"><Check size={20} /> Everything is cleared. FounderOS will surface the next action when it matters.</div> : actions.map((action) => <article className="approval-row" key={action.id}>
        <div className="approval-icon"><FileText size={18} /></div>
        <div className="approval-copy">
          <div>
            <h3>{action.title}</h3>
            <span className={`status ${action.status.toLowerCase()}`}>{action.status}</span>
          </div>
          <p>{action.detail}</p>
          <small>{action.source}</small>
        </div>
        <div className="approval-actions">
          <button className="secondary-button" onClick={() => onPreview(action)}>Preview</button>
          <button className="primary-button" onClick={() => onApprove(action.id)}>Approve <Check size={15} /></button>
        </div>
      </article>)}
    </section>
  </div>
}

function Focus({ index, title, detail }: { index: string; title: string; detail: string }) { return <div className="focus-item"><span className="focus-index">{index}</span><div><strong>{title}</strong><small>{detail}</small></div><ChevronRight size={16} /></div> }

function Decisions({ decisions, onOpenDebate, onNewDecision }: { decisions: Workspace['decisions']; onOpenDebate: (title: string) => void; onNewDecision: () => void }) {
  const displayDecisions = decisions && decisions.length > 0 ? decisions : [
    { id: 1, decisionCode: '#024', title: 'Pause Feature B and investigate activation', detail: 'Decision due Friday · High evidence · Click to debate', status: 'Open' },
    { id: 2, decisionCode: '#023', title: 'Focus enterprise outreach on logistics', detail: 'Decided July 28 · Pipeline +18% · Click to debate', status: 'Validated' },
    { id: 3, decisionCode: '#022', title: 'Move support ownership into Product', detail: 'Decided July 14 · Review Aug 14 · Click to debate', status: 'Learning' }
  ]

  return <div className="page simple-page">
    <div className="simple-heading">
      <div>
        <p className="eyebrow">INSTITUTIONAL MEMORY</p>
        <h1>Decision ledger</h1>
        <p className="subhead">A record of choices, assumptions, and learning. Click any decision to trigger an AI Executive Board debate.</p>
      </div>
      <button className="primary-button" onClick={onNewDecision}><Plus size={16} /> New decision</button>
    </div>
    <div className="ledger-card">
      {displayDecisions.map((d: any) => <div key={d.id} onClick={() => onOpenDebate(d.title)} style={{ cursor: 'pointer' }}>
        <Ledger id={d.decisionCode || `#0${d.id}`} title={d.title} detail={d.detail} status={d.status || 'Open'} />
      </div>)}
    </div>
  </div>
}

function Ledger({ id, title, detail, status }: { id: string; title: string; detail: string; status: string }) {
  const statusClass = status.toLowerCase().includes('open') ? 'open' : status.toLowerCase().includes('validated') ? 'validated' : 'learning'
  return <div className="ledger-row">
    <span className="decision-id">{id}</span>
    <div>
      <h3>{title}</h3>
      <p>{detail}</p>
    </div>
    <span className={`decision-status ${statusClass}`}>{status}</span>
    <ChevronRight size={18} />
  </div>
}

function MorningBriefingModal({ data, onClose, onDebate }: { data: any; onClose: () => void; onDebate: (title: string) => void }) {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [onClose])

  if (!data) return null
  return (
    <div className="modal-backdrop" role="presentation" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <section className="editor-modal" style={{ maxWidth: '680px', maxHeight: '85vh', overflowY: 'auto' }} role="dialog" aria-modal="true">
        <div className="modal-header">
          <div>
            <p className="eyebrow"><Sun size={14} style={{ color: '#d97706' }} /> EXECUTIVE MORNING BRIEFING</p>
            <h2>{data.date || 'Today\'s Briefing'}</h2>
          </div>
          <button className="icon-button" onClick={onClose} aria-label="Close modal"><X size={18} /></button>
        </div>

        <div style={{ background: '#f8fafc', padding: '14px 16px', borderRadius: '10px', border: '1px solid #e2e8f0', margin: '14px 0' }}>
          <strong style={{ color: '#0f172a', fontSize: '0.85rem' }}>Executive Overview</strong>
          <p style={{ margin: '6px 0 0', fontSize: '0.88rem', color: '#334155', lineHeight: '1.5' }}>
            {data.executiveSummary}
          </p>
        </div>

        <div style={{ margin: '14px 0' }}>
          <span className="section-kicker" style={{ fontSize: '11px', color: '#64748b' }}>OVERNIGHT HIGHLIGHTS & SIGNAL SYNTHESIS</span>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '6px' }}>
            {data.overnightChanges?.map((item: string, idx: number) => (
              <div key={idx} style={{ background: '#ffffff', padding: '10px 14px', borderRadius: '8px', border: '1px solid #e2e8f0', fontSize: '12px', color: '#1e293b', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <CheckCircle2 size={14} style={{ color: '#16a34a', flexShrink: 0 }} />
                <span>{item}</span>
              </div>
            ))}
          </div>
        </div>

        <div style={{ background: '#eff6ff', padding: '12px 14px', borderRadius: '8px', border: '1px solid #bfdbfe', color: '#1e40af', fontSize: '12px', margin: '12px 0' }}>
          <strong>One Metric That Matters (OMTM):</strong> {data.omtmStatus}
        </div>

        <div style={{ background: '#f0fdf4', padding: '14px', borderRadius: '8px', border: '1px solid #bbf7d0', color: '#15803d', fontSize: '12px', margin: '12px 0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <strong>Today's Highest Leverage Focus:</strong>
            <div style={{ fontSize: '13px', fontWeight: 700, color: '#166534', marginTop: '2px' }}>{data.topPriorityFocus}</div>
          </div>
          <button className="primary-button" style={{ fontSize: '11px', padding: '6px 12px' }} onClick={() => {
            onClose()
            onDebate(data.topPriorityFocus)
          }}>
            Debate Action <ArrowUpRight size={12} />
          </button>
        </div>

        {data.energyAdvice && (
          <div style={{ background: '#fefce8', padding: '10px 14px', borderRadius: '8px', border: '1px solid #fef08a', color: '#854d0e', fontSize: '11px', margin: '10px 0' }}>
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

function DebateModal({ data, onClose }: { data: any; onClose: () => void }) {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [onClose])

  if (!data) return null
  return (
    <div className="modal-backdrop" role="presentation" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <section className="editor-modal" style={{ maxWidth: '680px', maxHeight: '85vh', overflowY: 'auto' }} role="dialog" aria-modal="true">
        <div className="modal-header">
          <div>
            <p className="eyebrow"><Sparkles size={14} /> PEAK C-SUITE EXECUTIVE BOARD DEBATE</p>
            <h2>{data.decisionTitle}</h2>
          </div>
          <button className="icon-button" onClick={onClose} aria-label="Close modal"><X size={18} /></button>
        </div>
        
        {data.decisionFramework && (
          <div style={{ background: '#f1f5f9', padding: '8px 12px', borderRadius: '6px', fontSize: '11px', fontWeight: 600, color: '#475569', display: 'flex', alignItems: 'center', gap: '6px', margin: '10px 0' }}>
            <Compass size={13} style={{ color: '#2563eb' }} />
            <span>Framework: <strong>{data.decisionFramework}</strong></span>
          </div>
        )}

        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', margin: '14px 0' }}>
          {data.executivePerspectives?.map((item: any) => (
            <div key={item.lens} style={{ background: '#f8fafc', padding: '14px 16px', borderRadius: '10px', border: '1px solid #e2e8f0' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                <div>
                  <strong style={{ color: '#0f172a', fontSize: '0.85rem' }}>{item.lens}</strong>
                  <span style={{ marginLeft: '8px', color: item.stance === 'Support' ? '#15803d' : item.stance === 'Oppose' ? '#b91c1c' : '#d97706', fontSize: '0.8rem', fontWeight: 700, padding: '2px 6px', borderRadius: '4px', background: item.stance === 'Support' ? '#dcfce7' : item.stance === 'Oppose' ? '#fee2e2' : '#fef3c7' }}>
                    {item.stance}
                  </span>
                </div>
                {item.mentalModel && (
                  <span style={{ fontSize: '11px', color: '#64748b', background: '#ffffff', padding: '2px 8px', borderRadius: '12px', border: '1px solid #cbd5e1' }}>
                    🧠 {item.mentalModel}
                  </span>
                )}
              </div>
              <p style={{ margin: '6px 0 6px', fontSize: '0.88rem', color: '#1e293b', lineHeight: '1.45' }}>{item.argument}</p>
              <small style={{ color: '#64748b', fontSize: '11px', fontWeight: 600 }}>Key Tracked Metric: {item.keyMetric}</small>
            </div>
          ))}
        </div>

        {data.keyTradeoff && (
          <div style={{ background: '#fff7ed', padding: '10px 14px', borderRadius: '8px', border: '1px solid #ffedd5', color: '#c2410c', fontSize: '12px', marginBottom: '10px' }}>
            <strong>Key Executive Tradeoff:</strong> {data.keyTradeoff}
          </div>
        )}

        {data.recommendedExperiment && (
          <div style={{ background: '#f0fdf4', padding: '12px 14px', borderRadius: '8px', border: '1px solid #bbf7d0', color: '#15803d', fontSize: '12px', marginBottom: '14px' }}>
            <strong style={{ display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '2px' }}><FlaskConical size={14} /> 2-Week Minimum Viable Experiment (MVE):</strong>
            {data.recommendedExperiment}
          </div>
        )}

        <div style={{ background: '#eff6ff', padding: '14px', borderRadius: '10px', border: '1px solid #bfdbfe', marginBottom: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <span style={{ fontSize: '11px', color: '#1d4ed8', textTransform: 'uppercase', fontWeight: 700 }}>CEO Consensus:</span>
            <div style={{ color: '#1e40af', fontSize: '1rem', fontWeight: 800 }}>{data.consensus}</div>
          </div>
          <span style={{ fontSize: '11px', background: '#ffffff', color: '#2563eb', padding: '3px 8px', borderRadius: '6px', fontWeight: 600, border: '1px solid #93c5fd' }}>
            Confidence: {data.confidence || 'High'}
          </span>
        </div>

        <div className="modal-footer">
          <button className="primary-button" onClick={onClose}>Close executive debate</button>
        </div>
      </section>
    </div>
  )
}

function NewDecisionModal({ onClose, onSave }: { onClose: () => void; onSave: (title: string, detail: string) => void }) {
  const [title, setTitle] = useState('')
  const [detail, setDetail] = useState('')

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [onClose])

  return <div className="modal-backdrop" role="presentation" onClick={(e) => e.target === e.currentTarget && onClose()}><section className="editor-modal" role="dialog" aria-modal="true"><div className="modal-header"><div><p className="eyebrow">INSTITUTIONAL MEMORY</p><h2>Record New Decision</h2></div><button className="icon-button" onClick={onClose} aria-label="Close modal"><X size={18} /></button></div><p className="modal-copy">Preserve decision choices, rationale, and review dates to prevent repeated debates.</p><div className="form-grid single editor-fields"><label className="field"><span>Decision title</span><input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="e.g. Expand sales team into Europe" /></label><label className="field"><span>Rationale & Detail</span><input value={detail} onChange={(e) => setDetail(e.target.value)} placeholder="e.g. Customer demand is high, pipeline +24%" /></label></div><div className="modal-footer"><button className="secondary-button" onClick={onClose}>Cancel</button><button className="primary-button" onClick={() => title && onSave(title, detail)}>Save decision <Check size={15} /></button></div></section></div>
}

function AskFounderOSModal({ onClose, onDebate }: { onClose: () => void; onDebate: (query: string) => void }) {
  const [prompt, setPrompt] = useState('')

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [onClose])

  return <div className="modal-backdrop" role="presentation" onClick={(e) => e.target === e.currentTarget && onClose()}>
    <section className="editor-modal" style={{ maxWidth: '580px' }} role="dialog" aria-modal="true">
      <div className="modal-header">
        <div>
          <p className="eyebrow"><Command size={14} /> ASK FOUNDEROS</p>
          <h2>Direct Founder Reasoning Prompt</h2>
        </div>
        <button className="icon-button" onClick={onClose}><X size={18} /></button>
      </div>
      <p className="modal-copy">Query your operating workspace or prompt the Executive Board over any choice.</p>
      
      <div style={{ display: 'flex', gap: '8px', margin: '16px 0' }}>
        <input
          autoFocus
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="e.g. Should we expand our logistics wedge or focus on activation?"
          style={{ flex: 1, padding: '12px 14px', borderRadius: '8px', border: '1px solid #cbd5e1', fontSize: '14px', outline: 'none' }}
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
          <li style={{ cursor: 'pointer', color: '#2563eb' }} onClick={() => onDebate("Pause Feature B and investigate activation")}>"Pause Feature B and investigate activation"</li>
          <li style={{ cursor: 'pointer', color: '#2563eb' }} onClick={() => onDebate("Should we hire a VP Sales for logistics outreach?")}>"Should we hire a VP Sales for logistics outreach?"</li>
        </ul>
      </div>
    </section>
  </div>
}

function PreviewActionModal({ action, onClose, onApprove }: { action: any; onClose: () => void; onApprove: (id: number) => void }) {
  return <div className="modal-backdrop" role="presentation" onClick={(e) => e.target === e.currentTarget && onClose()}>
    <section className="editor-modal" style={{ maxWidth: '540px' }} role="dialog" aria-modal="true">
      <div className="modal-header">
        <div>
          <p className="eyebrow"><ShieldCheck size={14} /> ACTION PREVIEW & POLICY CHECK</p>
          <h2>{action.title}</h2>
        </div>
        <button className="icon-button" onClick={onClose}><X size={18} /></button>
      </div>
      <div style={{ background: '#f8fafc', padding: '14px', borderRadius: '8px', border: '1px solid #e2e8f0', margin: '14px 0' }}>
        <p style={{ margin: 0, fontSize: '13px', color: '#1e293b' }}>{action.detail}</p>
        <small style={{ display: 'block', marginTop: '8px', color: '#64748b', fontFamily: 'var(--font-mono)' }}>Source Platform: {action.source}</small>
      </div>
      <div style={{ background: '#dcfce7', padding: '10px 12px', borderRadius: '6px', border: '1px solid #86efac', color: '#15803d', fontSize: '12px', marginBottom: '16px' }}>
        <strong>Policy Engine Check:</strong> Passed domain allow-list and risk level verification. Draft dispatch enabled upon approval.
      </div>
      <div className="modal-footer">
        <button className="secondary-button" onClick={onClose}>Close preview</button>
        <button className="primary-button" onClick={() => onApprove(action.id)}>Approve & Dispatch <Check size={15} /></button>
      </div>
    </section>
  </div>
}

function SignalModal({ signal, onClose, onDebate }: { signal: any; onClose: () => void; onDebate: (title: string) => void }) {
  return <div className="modal-backdrop" role="presentation" onClick={(e) => e.target === e.currentTarget && onClose()}>
    <section className="editor-modal" style={{ maxWidth: '520px' }} role="dialog" aria-modal="true">
      <div className="modal-header">
        <div>
          <p className="eyebrow"><LineChart size={14} /> SIGNAL ANALYSIS</p>
          <h2>{signal.title}</h2>
        </div>
        <button className="icon-button" onClick={onClose}><X size={18} /></button>
      </div>
      <div style={{ background: '#f8fafc', padding: '14px', borderRadius: '8px', border: '1px solid #e2e8f0', margin: '14px 0' }}>
        <p style={{ margin: 0, fontSize: '13px', color: '#1e293b' }}>{signal.body}</p>
        <small style={{ display: 'block', marginTop: '8px', color: '#64748b' }}>Signal Category: <strong>{signal.tag}</strong></small>
      </div>
      <div className="modal-footer">
        <button className="secondary-button" onClick={onClose}>Dismiss</button>
        <button className="primary-button" onClick={() => onDebate(signal.title)}>Debate Signal Impact <ArrowUpRight size={15} /></button>
      </div>
    </section>
  </div>
}

function NotificationsDropdown({ onClose }: { onClose: () => void }) {
  return <div className="toast" style={{ top: '68px', right: '40px', width: '320px', flexDirection: 'column', alignItems: 'flex-start' }}>
    <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%', borderBottom: '1px solid #334155', paddingBottom: '8px', marginBottom: '8px' }}>
      <strong>System Notifications</strong>
      <button onClick={onClose} style={{ background: 'none', border: 0, color: '#94a3b8', cursor: 'pointer' }}><X size={14} /></button>
    </div>
    <div style={{ fontSize: '12px', color: '#cbd5e1', lineHeight: '1.5' }}>
      <div>✓ Worker: Background signal ingestion complete (3 items).</div>
      <div style={{ marginTop: '6px' }}>✓ Scheduler: Decision ledger review dates verified.</div>
      <div style={{ marginTop: '6px' }}>✓ Vault: AES-256-GCM token encryption active.</div>
    </div>
  </div>
}

function Intelligence({ onSelectSignal }: { onSelectSignal: (s: any) => void }) {
  return <div className="page simple-page">
    <div className="simple-heading">
      <div>
        <p className="eyebrow">OBSERVATION LAYER</p>
        <h1>Company intelligence</h1>
        <p className="subhead">Signals are ranked by impact, then connected to goals and decisions.</p>
      </div>
      <button className="secondary-button" onClick={() => onSelectSignal(signals[0])}><Plus size={16} /> Add watchlist</button>
    </div>
    <div className="intel-layout">
      <article className="card intel-card">
        <span className="section-kicker"><LineChart size={14} /> OPPORTUNITY RADAR</span>
        <h2>Logistics is becoming your clearest wedge.</h2>
        <p>Three qualified opportunities, two recent customer requests, and a competitor gap point to a focused enterprise test.</p>
        <div className="radar-score">
          <span>Opportunity score</span>
          <strong>78 <small>/ 100</small></strong>
        </div>
      </article>
      <article className="card watch-card">
        <span className="section-kicker"><Bell size={14} /> WATCHLIST</span>
        <div className="watch-item" style={{ cursor: 'pointer' }} onClick={() => onSelectSignal(signals[2])}><span className="watch-dot purple" />Enterprise competitor pricing changes</div>
        <div className="watch-item" style={{ cursor: 'pointer' }} onClick={() => onSelectSignal(signals[1])}><span className="watch-dot orange" />Activation completion below 60%</div>
        <div className="watch-item" style={{ cursor: 'pointer' }} onClick={() => onSelectSignal(signals[0])}><span className="watch-dot green" />Logistics customer mentions</div>
      </article>
    </div>
  </div>
}

function Company({ company, connectedCount, onEdit, onConnections }: { company: CompanyProfile; connectedCount: number; onEdit: () => void; onConnections: () => void }) {
  return <div className="page simple-page">
    <div className="simple-heading">
      <div>
        <p className="eyebrow">COMPANY MODEL</p>
        <h1>{company.name}</h1>
        <p className="subhead">The shared operating context that grounds every recommendation.</p>
      </div>
      <button className="secondary-button" onClick={onEdit}>Edit company model</button>
    </div>
    <div className="company-grid">
      <article className="card model-card">
        <span>Business model</span><strong>{company.businessModel}</strong>
        <span>Funding</span><strong>{company.fundingState}</strong>
        <span>Platform</span><strong>{company.platformFocus}</strong>
        <span>Stage</span><strong>{company.stage}</strong>
      </article>
      <article className="card model-card">
        <span>Current objective</span><strong>{company.objective}</strong>
        <span>Primary constraint</span><strong>{company.primaryConstraint}</strong>
        <span>Primary Metric</span><strong>{company.primaryMetric}</strong>
        <span>Runway floor</span><strong>{company.runwayMonths} months</strong>
      </article>
      <article className="card model-card">
        <span>Connected sources</span>
        <strong>{connectedCount ? `${connectedCount} source${connectedCount > 1 ? 's' : ''} configured` : 'No sources configured'}</strong>
        <p className="model-caption">Sources add evidence; they never receive execution access by default.</p>
        <button className="text-button" onClick={onConnections}>Manage sources <ChevronRight size={16} /></button>
      </article>
    </div>
  </div>
}

function Connections({ connectors, onConfigure }: { connectors: Connector[]; onConfigure: (id: ConnectorId) => void }) {
  return <div className="page simple-page">
    <div className="simple-heading">
      <div>
        <p className="eyebrow">INTEGRATION LAYER</p>
        <h1>Connections</h1>
        <p className="subhead">Choose the trusted company systems that can inform your operating brief.</p>
      </div>
      <span className="approval-note"><ShieldCheck size={15} /> Read access first</span>
    </div>
    <section className="connection-note">
      <Database size={18} />
      <div>
        <strong>Connection setup is local and intentional.</strong>
        <p>This prototype records your chosen sources only. Real data access will require per-service OAuth, scoped credentials, and an audit trail.</p>
      </div>
    </section>
    <section className="connection-grid">
      {connectors.map((connector) => <article className="connection-card" key={connector.id}>
        <div className="connection-icon">{connector.id === 'gmail' ? <Mail size={19} /> : connector.id === 'linear' ? <CircleDot size={19} /> : <Plug size={19} />}</div>
        <div className="connection-copy">
          <span>{connector.category}</span>
          <h3>{connector.name}</h3>
          <p>{connector.description}</p>
        </div>
        <div className="connection-footer">
          <div className={`connection-status ${connector.status}`}>
            {connector.status === 'configured' ? <CheckCircle2 size={14} /> : <CircleDot size={14} />}
            {connector.status === 'configured' ? 'Setup saved' : 'Not connected'}
          </div>
          <button className={connector.status === 'configured' ? 'secondary-button' : 'primary-button'} onClick={() => onConfigure(connector.id)}>
            {connector.status === 'configured' ? 'Review setup' : 'Set up'} <ChevronRight size={14} />
          </button>
        </div>
      </article>)}
    </section>
  </div>
}

function CompanyEditor({ company, onSave, onClose }: { company: CompanyProfile; onSave: (company: CompanyProfile) => void; onClose: () => void }) {
  const [draft, setDraft] = useState(company)
  const update = (field: keyof CompanyProfile, value: any) => setDraft((current) => ({ ...current, [field]: value }))
  
  const businessModels = ['B2B SaaS', 'B2C / D2C', 'Marketplace', 'Agency / Services', 'Hardware / Manufacturing', 'Open Source', 'Other']
  const platformFocuses = ['Web Application', 'Mobile App', 'API / Developer Tools', 'Chrome Extension', 'Offline / Retail', 'Other']
  const fundingStates = ['Bootstrapped', 'Pre-Seed', 'Seed', 'Series A', 'Series B+', 'Public']
  const revenueRanges = ['Pre-revenue', '<$10k MRR', '$10k-$100k MRR', '$1M+ ARR']
  const stages = ['Idea stage', 'Pre-revenue', 'Early revenue', 'Growth stage', 'Scale']
  const teamSizes = ['Solo founder', '2-5 people', '6-15 people', '16-50 people', '50+ people']
  
  return <div className="modal-backdrop" role="presentation" onClick={(e) => e.target === e.currentTarget && onClose()}>
    <section className="editor-modal" role="dialog" aria-modal="true" aria-label="Edit company model">
      <div className="modal-header">
        <div>
          <p className="eyebrow">COMPANY MODEL</p>
          <h2>Refine FounderOS’s context</h2>
        </div>
        <button className="icon-button" onClick={onClose} aria-label="Close editor"><X size={18} /></button>
      </div>
      <p className="modal-copy">These fields influence how the system ranks trade-offs and recommendations.</p>
      <div className="form-grid single editor-fields" style={{ maxHeight: '60vh', overflowY: 'auto', paddingRight: '10px' }}>
        <p className="eyebrow" style={{ marginTop: '16px' }}>Digital Footprint</p>
        <Field label="Website URL" value={draft.websiteUrl || ''} onChange={(value) => update('websiteUrl', value)} />
        <Field label="LinkedIn Profile" value={draft.linkedinUrl || ''} onChange={(value) => update('linkedinUrl', value)} />
        <Field label="Social Profile" value={draft.socialUrl || ''} onChange={(value) => update('socialUrl', value)} />
        
        <p className="eyebrow" style={{ marginTop: '16px' }}>Architecture & Scale</p>
        <SelectField label="Business Model" value={draft.businessModel || ''} options={businessModels} onChange={(value) => update('businessModel', value)} />
        <SelectField label="Platform Focus" value={draft.platformFocus || ''} options={platformFocuses} onChange={(value) => update('platformFocus', value)} />
        <SelectField label="Funding State" value={draft.fundingState || ''} options={fundingStates} onChange={(value) => update('fundingState', value)} />
        <SelectField label="Revenue Range" value={draft.revenueRange || ''} options={revenueRanges} onChange={(value) => update('revenueRange', value)} />
        <SelectField label="Stage" value={draft.stage} options={stages} onChange={(value) => update('stage', value)} />
        <SelectField label="Team Size" value={draft.teamSize} options={teamSizes} onChange={(value) => update('teamSize', value)} />
        
        <p className="eyebrow" style={{ marginTop: '16px' }}>Strategic Compass</p>
        <Field label="Current objective" value={draft.objective} onChange={(value) => update('objective', value)} />
        <Field label="Ideal customer" value={draft.idealCustomer} onChange={(value) => update('idealCustomer', value)} />
        <Field label="Primary Metric" value={draft.primaryMetric} onChange={(value) => update('primaryMetric', value)} />
        <Field label="Primary constraint" value={draft.primaryConstraint} onChange={(value) => update('primaryConstraint', value)} />
        <NumberField label="Runway (months)" value={draft.runwayMonths} onChange={(value) => update('runwayMonths', value)} />
        <Field label="GTM Motion" value={draft.gtmMotion || ''} onChange={(value) => update('gtmMotion', value)} />
        <Field label="Burn Rate" value={draft.burnRate || ''} onChange={(value) => update('burnRate', value)} />
        <Field label="Tech Stack" value={draft.techStack || ''} onChange={(value) => update('techStack', value)} />
        <Field label="Competitive Moat" value={draft.competitiveMoat || ''} onChange={(value) => update('competitiveMoat', value)} />
      </div>
      <div className="modal-footer">
        <button className="secondary-button" onClick={onClose}>Cancel</button>
        <button className="primary-button" onClick={() => onSave(draft)}>Save company model <Check size={15} /></button>
      </div>
    </section>
  </div>
}

function FounderEditor({ founder, onSave, onClose }: { founder: FounderProfile; onSave: (founder: FounderProfile) => void; onClose: () => void }) {
  const [draft, setDraft] = useState(founder)
  const update = (field: keyof FounderProfile, value: any) => setDraft((current) => ({ ...current, [field]: value }))
  
  const founderRoles = ['Solo Founder', 'CEO', 'CTO', 'COO', 'Other']
  const founderBackgrounds = ['Engineering / Technical', 'Product / Design', 'Sales / Go-to-Market', 'Operations / Finance', 'Marketing / Growth']
  const experienceLevels = ['First-time Founder', 'Second-time Founder', 'Serial Founder (3+)', 'Industry Veteran (10+ yrs)']
  const founderSuperpowers = ['Building & Engineering', 'Sales & Closing Deals', 'Product Vision & UX', 'Fundraising & Capital', 'Recruiting & Team Building']

  return <div className="modal-backdrop" role="presentation" onClick={(e) => e.target === e.currentTarget && onClose()}>
    <section className="editor-modal" role="dialog" aria-modal="true" aria-label="Edit founder profile">
      <div className="modal-header">
        <div>
          <p className="eyebrow">FOUNDER PROFILE</p>
          <h2>Who is driving the ship?</h2>
        </div>
        <button className="icon-button" onClick={onClose} aria-label="Close editor"><X size={18} /></button>
      </div>
      <p className="modal-copy">Update your strengths and gaps to receive better executive advice.</p>
      <div className="form-grid single editor-fields" style={{ maxHeight: '60vh', overflowY: 'auto', paddingRight: '10px' }}>
        <Field label="Your name" value={draft.name} onChange={(value) => update('name', value)} />
        <SelectField label="Role" value={draft.role} options={founderRoles} onChange={(value) => update('role', value)} />
        <SelectField label="Core Background" value={draft.background} options={founderBackgrounds} onChange={(value) => update('background', value)} />
        <SelectField label="Experience Level" value={draft.experienceLevel} options={experienceLevels} onChange={(value) => update('experienceLevel', value)} />
        <Field label="Domain Expertise (e.g. Fintech, Healthcare)" value={draft.domainExpertise} onChange={(value) => update('domainExpertise', value)} />
        <SelectField label="Your Superpower (Strongest skill)" value={draft.superpower} options={founderSuperpowers} onChange={(value) => update('superpower', value)} />
        <SelectField label="Your Primary Gap (Weakest skill)" value={draft.primaryGap} options={founderSuperpowers} onChange={(value) => update('primaryGap', value)} />
        <Field label="Current Learning Focus" value={draft.learningFocus} onChange={(value) => update('learningFocus', value)} />
        <Field label="Communication Style (e.g. Direct)" value={draft.communicationStyle || ''} onChange={(value) => update('communicationStyle', value)} />
        <Field label="Energy State (e.g. Burned out, High)" value={draft.energyState || ''} onChange={(value) => update('energyState', value)} />
        <Field label="Core Values (e.g. Speed, Quality)" value={draft.coreValues || ''} onChange={(value) => update('coreValues', value)} />
      </div>
      <div className="modal-footer">
        <button className="secondary-button" onClick={onClose}>Cancel</button>
        <button className="primary-button" onClick={() => onSave(draft)}>Save founder profile <Check size={15} /></button>
      </div>
    </section>
  </div>
}

function Field({ label, value, onChange }: { label: string; value: string; onChange: (value: string) => void }) {
  return <label className="field">
    <span>{label}</span>
    <input value={value} onChange={(event) => onChange(event.target.value)} />
  </label>
}

function NumberField({ label, value, onChange }: { label: string; value: number; onChange: (value: number) => void }) {
  return <label className="field">
    <span>{label}</span>
    <input type="number" min="0" value={value} onChange={(event) => onChange(parseInt(event.target.value) || 0)} />
  </label>
}

function SelectField({ label, value, options, onChange }: { label: string; value: string; options: string[]; onChange: (value: string) => void }) {
  return <label className="field">
    <span>{label}</span>
    <select value={value} onChange={(event) => onChange(event.target.value)}>
      {options.map(opt => <option key={opt} value={opt}>{opt}</option>)}
    </select>
  </label>
}

function ModelsView({ onNotice, onReset }: { onNotice: (msg: string) => void; onReset: () => void }) {
  const [data, setData] = useState<any>(null)
  const [selectedProvider, setSelectedProvider] = useState('anthropic')
  const [selectedModel, setSelectedModel] = useState('claude-opus-5')
  const [apiKey, setApiKey] = useState('')
  const [customBaseUrl, setCustomBaseUrl] = useState('')
  const [reasoningEffort, setReasoningEffort] = useState('max')
  const [showKey, setShowKey] = useState(false)
  const [testStatus, setTestStatus] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [discovering, setDiscovering] = useState(false)
  const [discoveredModels, setDiscoveredModels] = useState<string[]>([])

  const loadData = () => {
    fetchModelSettings().then((res) => {
      if (res) {
        setData(res)
        const active = res.providers?.find((p: any) => p.isActive)
        if (active) {
          setSelectedProvider(active.providerName)
          setSelectedModel(active.selectedModel)
          setCustomBaseUrl(active.customBaseUrl || '')
          setReasoningEffort(active.reasoningEffort || 'max')
        } else {
          const currentProv = res.providers?.find((p: any) => p.providerName === selectedProvider)
          if (currentProv) {
            setSelectedModel(currentProv.selectedModel)
            setCustomBaseUrl(currentProv.customBaseUrl || '')
            setReasoningEffort(currentProv.reasoningEffort || 'max')
          }
        }
      }
    })
  }

  useEffect(() => {
    loadData()
  }, [])

  const currentProviderInfo = data?.supportedProviders?.find((p: any) => p.name === selectedProvider)
  const configuredItem = data?.providers?.find((p: any) => p.providerName === selectedProvider)

  const handleProviderSelect = (prov: any) => {
    const item = data?.providers?.find((p: any) => p.providerName === prov.name)
    setSelectedProvider(prov.name)
    setSelectedModel(item?.selectedModel || prov.defaultModel)
    setCustomBaseUrl(item?.customBaseUrl || '')
    setReasoningEffort(item?.reasoningEffort || 'max')
    setDiscoveredModels([])
    setTestStatus(null)
  }

  const handleSave = async (isActive: boolean) => {
    setLoading(true)
    const ok = await saveModelSetting(
      selectedProvider,
      selectedModel,
      apiKey,
      isActive,
      customBaseUrl || undefined,
      reasoningEffort
    )
    setLoading(false)
    if (ok) {
      onNotice(`${currentProviderInfo?.label || selectedProvider} settings saved and encrypted in Vault.`)
      setApiKey('')
      loadData()
    }
  }

  const handleTest = async () => {
    setTestStatus('Testing connection live...')
    const res = await testModelConnection(
      selectedProvider,
      selectedModel,
      apiKey,
      customBaseUrl || undefined,
      reasoningEffort
    )
    setTestStatus(res.status)
  }

  const handleDiscover = async () => {
    setDiscovering(true)
    try {
      const res = await discoverProviderModels(selectedProvider, apiKey, customBaseUrl || undefined)
      if (res && res.models && res.models.length > 0) {
        setDiscoveredModels(res.models)
        if (!res.models.includes(selectedModel)) {
          setSelectedModel(res.models[0])
        }
        onNotice(`⚡ Auto-discovered ${res.count} live models from ${currentProviderInfo?.label || selectedProvider}!`)
      } else {
        onNotice('No new models returned. Using standard model catalog.')
      }
    } catch (e: any) {
      onNotice(`Model discovery notice: ${e.message || 'Could not query models endpoint'}`)
    } finally {
      setDiscovering(false)
    }
  }

  const availableModelList = discoveredModels.length > 0
    ? discoveredModels
    : (currentProviderInfo?.availableModels || [selectedModel])

  return <div className="page simple-page">
    <div className="simple-heading">
      <div>
        <p className="eyebrow">AI REASONING LAYER & UNIVERSAL CONNECTORS</p>
        <h1>Frontier Models & AI Connectors</h1>
        <p className="subhead">Hermes & OpenClaw style dynamic provider protocol. Connect Claude Opus/Fable 5, GPT-5.6 Sol/Luna, Grok 4.6, Kimi K3, Gemini 3.7, DeepSeek V4 Pro, GLM-5.2, or Nemotron 3 Ultra.</p>
      </div>
      <span className="approval-note"><ShieldCheck size={15} /> Encrypted Vault</span>
    </div>

    <div className="company-grid" style={{ marginBottom: '24px', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))' }}>
      {(data?.supportedProviders || [
        { name: 'anthropic', label: 'Anthropic Claude', defaultModel: 'claude-opus-5', description: 'Claude Opus 5 (max), Claude Fable 5 (with fallback), Claude Sonnet 5.' },
        { name: 'openai', label: 'OpenAI', defaultModel: 'gpt-5.6-sol', description: 'GPT-5.6 Sol (max), GPT-5.6 Luna (max), o3-mini (high), o1.' },
        { name: 'xai', label: 'xAI (Grok)', defaultModel: 'grok-4.6', description: 'Grok 4.6 (high/xhigh), Grok 4.5 — Uncensored contrarian debate.' },
        { name: 'kimi', label: 'Moonshot AI (Kimi)', defaultModel: 'kimi-k3', description: 'Kimi K3 (max 2.8T parameters, 1M context), Kimi K2.7 Code.' },
        { name: 'gemini', label: 'Google Gemini', defaultModel: 'gemini-3.7-flash', description: 'Gemini 3.7 Flash (high), Gemini 3.6 Flash, Gemini 3.1 Pro.' },
        { name: 'deepseek', label: 'DeepSeek', defaultModel: 'deepseek-v4-pro-0813', description: 'DeepSeek V4 Pro 0813 (max), DeepSeek Reasoner (R1), Chat (V3).' },
        { name: 'zhipu', label: 'Zhipu AI (GLM / Z.ai)', defaultModel: 'glm-5.2', description: 'GLM-5.2 (max), GLM-5V-Turbo — 1M context multimodal reasoning.' },
        { name: 'nvidia', label: 'NVIDIA NIM', defaultModel: 'nvidia/nemotron-3-ultra', description: 'Nemotron 3 Ultra, Nemotron 3.5 Lightning GPU microservices.' },
        { name: 'muse', label: 'Meta / Muse', defaultModel: 'muse-spark-1.2', description: 'Muse Spark 1.2 (xhigh), Llama 3.3 70B open-weights intelligence.' },
        { name: 'groq', label: 'Groq (Ultra-Fast LPUs)', defaultModel: 'llama-3.3-70b-versatile', description: '500+ tok/s instantaneous executive briefings & board debate.' },
        { name: 'openrouter', label: 'OpenRouter Gateway', defaultModel: 'anthropic/claude-opus-5', description: 'Universal gateway granting instant access to 200+ models.' },
        { name: 'ollama', label: 'Ollama / Local LLM', defaultModel: 'deepseek-r1:latest', description: '100% private, zero-data-leakage inference on local hardware.' },
        { name: 'custom', label: 'Custom OpenAI-Compatible', defaultModel: 'default', description: 'Self-hosted vLLM, LM Studio, or private OpenAI endpoint.' }
      ]).map((prov: any) => {
        const item = data?.providers?.find((p: any) => p.providerName === prov.name)
        const isSelected = selectedProvider === prov.name
        return <div
          key={prov.name}
          className={`card model-card ${isSelected ? 'selected' : ''}`}
          onClick={() => handleProviderSelect(prov)}
          style={{ cursor: 'pointer', border: isSelected ? '2px solid #0f172a' : '1px solid #e2e8f0', background: isSelected ? '#f8fafc' : '#ffffff', transition: 'all 0.15s ease' }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <strong style={{ fontSize: '1.05rem', color: '#0f172a' }}>{prov.label}</strong>
            {item?.isActive && <span style={{ background: '#dcfce7', color: '#15803d', fontSize: '0.75rem', padding: '2px 8px', borderRadius: '12px', fontWeight: 600 }}>Active</span>}
          </div>
          <p style={{ fontSize: '0.8rem', color: '#64748b', margin: '4px 0 8px', lineHeight: '1.3' }}>{prov.description || 'Frontier AI Provider'}</p>
          <span style={{ margin: '4px 0', fontSize: '0.82rem', color: '#475569', display: 'block' }}>Model: <strong style={{ color: '#0f172a' }}>{item?.selectedModel || prov.defaultModel}</strong></span>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.78rem', color: item?.hasKey || prov.name === 'ollama' ? '#16a34a' : '#94a3b8' }}>
            {item?.hasKey || prov.name === 'ollama' ? <CheckCircle2 size={13} /> : <CircleDot size={13} />}
            {prov.name === 'ollama' ? 'Local Connection' : (item?.hasKey ? `Key saved (${item.maskedApiKey})` : 'No key added')}
          </div>
        </div>
      })}
    </div>

    <section className="card editor-modal" style={{ maxWidth: '100%', margin: '0', background: '#ffffff', border: '1px solid #e2e8f0' }}>
      <div className="modal-header">
        <div>
          <p className="eyebrow"><Cpu size={14} /> CONFIGURE {currentProviderInfo?.label?.toUpperCase() || selectedProvider.toUpperCase()}</p>
          <h2>API Credentials & Cognitive Depth Config</h2>
        </div>
        <button
          className="secondary-button"
          onClick={handleDiscover}
          disabled={discovering}
          style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem' }}
        >
          <Sparkles size={14} /> {discovering ? 'Querying /v1/models...' : '⚡ Auto-Discover Live Models'}
        </button>
      </div>

      <div className="form-grid single editor-fields" style={{ margin: '16px 0' }}>
        <label className="field">
          <span>Select or Type Model {discoveredModels.length > 0 && <small style={{ color: '#16a34a', fontWeight: 600 }}>({discoveredModels.length} live models discovered from API)</small>}</span>
          <div style={{ display: 'flex', gap: '8px' }}>
            <select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              style={{ background: '#ffffff', color: '#0f172a', padding: '10px 12px', borderRadius: '8px', border: '1px solid #e2e8f0', fontSize: '13px', flex: 1.2 }}
            >
              {availableModelList.map((m: string) => <option key={m} value={m}>{m}</option>)}
            </select>
            <input
              type="text"
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              placeholder="Or custom model ID (e.g. claude-opus-5, gpt-5.6-sol)..."
              style={{ flex: 1, padding: '10px 12px', fontSize: '13px' }}
            />
          </div>
        </label>

        <label className="field">
          <span>Cognitive Depth & Reasoning Effort <small style={{ color: '#64748b' }}>(Controls multi-step deliberation level on C-Suite strategic debates)</small></span>
          <div style={{ display: 'flex', gap: '8px' }}>
            {[
              { id: 'max', label: 'Max (Deep Chain-of-Thought)' },
              { id: 'xhigh', label: 'X-High' },
              { id: 'high', label: 'High (Standard Executive)' },
              { id: 'medium', label: 'Medium' },
              { id: 'off', label: 'Instant (No Extended Thinking)' }
            ].map(tier => (
              <button
                key={tier.id}
                type="button"
                className={`secondary-button ${reasoningEffort === tier.id ? 'primary-button' : ''}`}
                onClick={() => setReasoningEffort(tier.id)}
                style={{ flex: 1, padding: '8px 4px', fontSize: '12px', textAlign: 'center' }}
              >
                {tier.label}
              </button>
            ))}
          </div>
        </label>

        <label className="field">
          <span>Custom Base URL <small style={{ color: '#64748b' }}>(Optional override for self-hosted vLLM, LM Studio, proxies, or Azure)</small></span>
          <input
            type="text"
            value={customBaseUrl}
            onChange={(e) => setCustomBaseUrl(e.target.value)}
            placeholder={currentProviderInfo?.defaultBaseUrl || 'e.g. https://api.openai.com/v1'}
            style={{ width: '100%', fontSize: '13px' }}
          />
        </label>

        {selectedProvider !== 'ollama' && <label className="field">
          <span>API Key {configuredItem?.hasKey && <small style={{ color: '#71717a' }}>(Saved: {configuredItem.maskedApiKey})</small>}</span>
          <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
            <input
              type={showKey ? 'text' : 'password'}
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder={configuredItem?.hasKey ? 'Leave blank to keep existing key, or paste new key' : 'Paste API key here...'}
              style={{ width: '100%', paddingRight: '40px' }}
            />
            <button
              type="button"
              onClick={() => setShowKey(!showKey)}
              style={{ position: 'absolute', right: '10px', background: 'none', border: 'none', color: '#a1a1aa', cursor: 'pointer' }}
            >
              {showKey ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          </div>
        </label>}
      </div>

      {testStatus && <div style={{ marginBottom: '16px', padding: '10px 14px', borderRadius: '8px', background: testStatus.includes('✓') ? 'rgba(34,197,94,0.1)' : 'rgba(239,68,68,0.1)', border: testStatus.includes('✓') ? '1px solid rgba(34,197,94,0.3)' : '1px solid rgba(239,68,68,0.3)', color: testStatus.includes('✓') ? '#16a34a' : '#dc2626', fontSize: '0.9rem' }}>
        <strong>Status:</strong> {testStatus}
      </div>}

      <div className="modal-footer" style={{ justifyContent: 'space-between' }}>
        <button className="secondary-button" onClick={handleTest}>
          Test connection
        </button>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button className="secondary-button" onClick={() => handleSave(false)} disabled={loading}>
            Save credentials
          </button>
          <button className="primary-button" onClick={() => handleSave(true)} disabled={loading}>
            Save & set active <Check size={15} />
          </button>
        </div>
      </div>
    </section>

    <section className="card editor-modal" style={{ maxWidth: '100%', marginTop: '24px', background: '#ffffff', border: '1px solid #e2e8f0' }}>
      <div className="modal-header">
        <div>
          <p className="eyebrow"><ShieldCheck size={14} style={{ color: '#2563eb' }} /> SECURITY POSTURE & ACTION POLICY (YC QM STANDARD)</p>
          <h2>Execution Safety Gates</h2>
          <p className="subhead">Govern how autonomous agent tasks and draft actions are staged and executed.</p>
        </div>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px', margin: '16px 0' }}>
        <div style={{ padding: '12px 14px', borderRadius: '8px', border: '2px solid #2563eb', background: '#eff6ff' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
            <strong style={{ fontSize: '0.85rem', color: '#1e40af' }}>Auto (Default)</strong>
            <span style={{ fontSize: '10px', background: '#dbeafe', color: '#1d4ed8', padding: '1px 6px', borderRadius: '4px', fontWeight: 700 }}>ACTIVE</span>
          </div>
          <p style={{ margin: 0, fontSize: '11px', color: '#3b82f6', lineHeight: '1.4' }}>
            Inbound text is screened for prompt injection. Safe action drafts are auto-staged for review.
          </p>
        </div>
        <div style={{ padding: '12px 14px', borderRadius: '8px', border: '1px solid #cbd5e1', background: '#f8fafc' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
            <strong style={{ fontSize: '0.85rem', color: '#334155' }}>Strict</strong>
          </div>
          <p style={{ margin: 0, fontSize: '11px', color: '#64748b', lineHeight: '1.4' }}>
            Every autonomous task and tool call pauses for explicit human-in-the-loop sign-off.
          </p>
        </div>
        <div style={{ padding: '12px 14px', borderRadius: '8px', border: '1px solid #cbd5e1', background: '#f8fafc' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
            <strong style={{ fontSize: '0.85rem', color: '#334155' }}>Dangerous</strong>
          </div>
          <p style={{ margin: 0, fontSize: '11px', color: '#64748b', lineHeight: '1.4' }}>
            Autonomous tool execution without human confirmation (for sandbox testing).
          </p>
        </div>
      </div>
      <div style={{ background: '#f8fafc', padding: '10px 14px', borderRadius: '6px', fontSize: '11px', color: '#475569', border: '1px solid #e2e8f0' }}>
        <strong>Command & Action Policy Filter:</strong> Active rules intercept destructive SQL (DROP TABLE), recursive deletes (rm -rf), force pushes, and secret exposure.
      </div>
    </section>

    <section className="card editor-modal danger-zone" style={{ maxWidth: '100%', marginTop: '32px', background: '#ffffff', border: '1px solid #fecaca' }}>
      <div className="modal-header">
        <div>
          <p className="eyebrow" style={{ color: '#ef4444' }}><Flame size={14} /> DANGER ZONE</p>
          <h2>Reset Workspace</h2>
          <p className="subhead">This will permanently delete all company data, founder context, agent action history, and vector embeddings from the FounderOS database.</p>
        </div>
      </div>
      <div className="modal-footer" style={{ justifyContent: 'flex-start' }}>
        <button className="primary-button" style={{ background: '#ef4444', color: 'white', border: 'none' }} onClick={onReset}>
          Delete Profile & Start Fresh
        </button>
      </div>
    </section>
  </div>
}

function TasksView({ tasks, onScan, onNewTask, onDelegate, onComplete }: {
  tasks: any[];
  onScan: () => void;
  onNewTask: () => void;
  onDelegate: (id: number) => void;
  onComplete: (id: number) => void;
}) {
  const [selectedCategory, setSelectedCategory] = useState<'TODAY' | 'UPCOMING' | 'DELEGATED' | 'COMPLETED' | 'ALL'>('TODAY')
  const [selectedPriority, setSelectedPriority] = useState<string>('ALL')

  const defaultTasks = [
    {
      id: 1,
      title: 'Review Enterprise SLA clause for Atlas Logistics contract',
      description: 'Incoming email from Atlas legal requests custom 99.9% uptime SLA response before 5 PM.',
      priority: 'P0_CRITICAL',
      category: 'TODAY',
      source: 'EMAIL',
      status: 'PENDING',
      due_date: 'Today 5:00 PM',
      agent_note: 'Discovered from Gmail monitoring. Flagged P0 due to deal size ($120k ARR).'
    },
    {
      id: 2,
      title: 'Approve activation funnel patch on Linear issue #LIN-284',
      description: 'Linear issue created by Product lead regarding first-value completion drop.',
      priority: 'P1_HIGH',
      category: 'TODAY',
      source: 'LINEAR',
      status: 'PENDING',
      due_date: 'Today',
      agent_note: 'Discovered from Linear integration webhook.'
    },
    {
      id: 3,
      title: 'Prepare discovery call notes for Sequoia Partner sync',
      description: 'Calendar event tomorrow at 10:00 AM. Agent extracted metric pitch deck highlights.',
      priority: 'P1_HIGH',
      category: 'UPCOMING',
      source: 'CALENDAR',
      status: 'PENDING',
      due_date: 'Tomorrow 10:00 AM',
      agent_note: 'Discovered from Google Calendar sync.'
    },
    {
      id: 4,
      title: 'Draft investor monthly update pre-read',
      description: 'Monthly update draft generated by agent with July MRR growth & runway floor.',
      priority: 'P2_MEDIUM',
      category: 'DELEGATED',
      source: 'AGENT_MONITOR',
      status: 'DELEGATED',
      due_date: 'Friday',
      agent_note: 'Delegated to FounderOS Agent. Draft ready for review.'
    }
  ]

  const displayTasks = tasks && tasks.length > 0 ? tasks : defaultTasks

  const filteredTasks = displayTasks.filter((task: any) => {
    if (selectedCategory === 'TODAY' && task.category !== 'TODAY') return false
    if (selectedCategory === 'UPCOMING' && task.category !== 'UPCOMING') return false
    if (selectedCategory === 'DELEGATED' && task.category !== 'DELEGATED' && task.status !== 'DELEGATED') return false
    if (selectedCategory === 'COMPLETED' && task.status !== 'COMPLETED') return false
    if (selectedPriority !== 'ALL' && task.priority !== selectedPriority) return false
    return true
  })

  // Metric counts
  const todayCount = displayTasks.filter((t: any) => t.category === 'TODAY' && t.status !== 'COMPLETED').length
  const p0Count = displayTasks.filter((t: any) => t.priority === 'P0_CRITICAL' && t.status !== 'COMPLETED').length
  const delegatedCount = displayTasks.filter((t: any) => t.status === 'DELEGATED' || t.category === 'DELEGATED').length

  return <div className="page simple-page">
    <div className="simple-heading">
      <div>
        <p className="eyebrow">FOUNDER WORKFLOW ENGINE</p>
        <h1>Founder Tasks & Delegation</h1>
        <p className="subhead">Tasks automatically synthesized from monitored emails, calendar, Linear, and system alerts.</p>
      </div>
      <div style={{ display: 'flex', gap: '10px' }}>
        <button className="secondary-button" onClick={onScan}>
          <Sparkles size={16} /> ⚡ Scan Monitored Systems
        </button>
        <button className="primary-button" onClick={onNewTask}>
          <Plus size={16} /> New Task
        </button>
      </div>
    </div>

    {/* Metric Summary Strip */}
    <div className="health-strip" style={{ gridTemplateColumns: '1.2fr 1fr 1fr 1fr', marginBottom: '24px' }}>
      <div className="health-main">
        <div className="pulse-ring"><span>{todayCount}</span></div>
        <div>
          <p>TODAY'S WORK PLAN</p>
          <strong>{todayCount} Priority Tasks Due Today</strong>
          <small><span className="up">Synthesized by Agent</span></small>
        </div>
      </div>
      <div className="health-stat">
        <span>P0 Critical</span>
        <strong style={{ color: p0Count > 0 ? '#dc2626' : '#0f172a' }}>0{p0Count}</strong>
        <i className={p0Count > 0 ? 'attention' : 'stable'}>{p0Count > 0 ? 'Requires Immediate Founder Action' : 'All Clear'}</i>
      </div>
      <div className="health-stat">
        <span>Delegated to Agent</span>
        <strong>0{delegatedCount}</strong>
        <i className="stable">Autonomous Execution</i>
      </div>
      <div className="health-stat">
        <span>Monitored Sources</span>
        <strong>04</strong>
        <i className="stable">Gmail, Calendar, Linear, Alerts</i>
      </div>
    </div>

    {/* Control Filter Bar */}
    <div className="card" style={{ padding: '14px 20px', marginBottom: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
      <div style={{ display: 'flex', gap: '6px' }}>
        {(['TODAY', 'UPCOMING', 'DELEGATED', 'COMPLETED', 'ALL'] as const).map((cat) => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`secondary-button ${selectedCategory === cat ? 'active' : ''}`}
            style={{
              height: '32px',
              fontSize: '12px',
              background: selectedCategory === cat ? '#0f172a' : '#ffffff',
              color: selectedCategory === cat ? '#ffffff' : '#475569',
              borderColor: selectedCategory === cat ? '#0f172a' : '#e2e8f0',
              fontWeight: selectedCategory === cat ? 600 : 500
            }}
          >
            {cat === 'TODAY' ? 'Today' : cat === 'UPCOMING' ? 'Upcoming' : cat === 'DELEGATED' ? 'Delegated to Agent' : cat === 'COMPLETED' ? 'Completed' : 'All Tasks'}
          </button>
        ))}
      </div>

      <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
        <span style={{ fontSize: '12px', color: '#64748b', fontWeight: 600 }}>Priority:</span>
        <select
          value={selectedPriority}
          onChange={(e) => setSelectedPriority(e.target.value)}
          style={{ padding: '6px 10px', borderRadius: '6px', border: '1px solid #cbd5e1', fontSize: '12px', outline: 'none', background: '#ffffff', color: '#0f172a' }}
        >
          <option value="ALL">All Priorities</option>
          <option value="P0_CRITICAL">P0 Critical</option>
          <option value="P1_HIGH">P1 High</option>
          <option value="P2_MEDIUM">P2 Medium</option>
          <option value="P3_LOW">P3 Low</option>
        </select>
      </div>
    </div>

    {/* Task List */}
    <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
      {filteredTasks.length === 0 ? (
        <div className="card" style={{ padding: '40px', textAlign: 'center', color: '#64748b' }}>
          <CheckCircle2 size={32} style={{ color: '#16a34a', marginBottom: '10px' }} />
          <h3>No tasks in this view</h3>
          <p style={{ margin: '4px 0 0', fontSize: '13px' }}>Your founder work plan is completely clear. Click "Scan Monitored Systems" to let FounderOS discover upcoming items.</p>
        </div>
      ) : (
        filteredTasks.map((task: any) => {
          const isP0 = task.priority === 'P0_CRITICAL'
          const isP1 = task.priority === 'P1_HIGH'
          const isP2 = task.priority === 'P2_MEDIUM'

          const badgeBg = isP0 ? '#fee2e2' : isP1 ? '#fef3c7' : isP2 ? '#e0e7ff' : '#f1f5f9'
          const badgeText = isP0 ? '#b91c1c' : isP1 ? '#b45309' : isP2 ? '#4338ca' : '#475569'
          const badgeBorder = isP0 ? '#f87171' : isP1 ? '#fde68a' : isP2 ? '#c7d2fe' : '#e2e8f0'

          return (
            <article className="card" key={task.id} style={{ padding: '20px 24px', borderLeft: isP0 ? '4px solid #dc2626' : isP1 ? '4px solid #f59e0b' : '1px solid #e2e8f0' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span style={{ background: badgeBg, color: badgeText, border: `1px solid ${badgeBorder}`, padding: '3px 8px', borderRadius: '6px', fontSize: '11px', fontWeight: 700, fontFamily: 'var(--font-mono)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                    {isP0 && <Flame size={12} />}
                    {task.priority.replace('_', ' ')}
                  </span>
                  <span style={{ background: '#f1f5f9', color: '#64748b', padding: '3px 8px', borderRadius: '6px', fontSize: '11px', fontWeight: 600, fontFamily: 'var(--font-mono)' }}>
                    {task.source}
                  </span>
                  {task.due_date && <span style={{ color: '#64748b', fontSize: '12px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <Clock size={13} /> {task.due_date}
                  </span>}
                </div>

                <div style={{ display: 'flex', gap: '8px' }}>
                  {task.status !== 'COMPLETED' && task.status !== 'DELEGATED' && task.status !== 'FAILED' && (
                    <button className="secondary-button" onClick={() => onDelegate(task.id)} style={{ height: '30px', fontSize: '12px' }}>
                      <Bot size={14} /> Delegate to Agent
                    </button>
                  )}
                  {task.status === 'DELEGATED' && (
                    <span style={{ background: '#dcfce7', color: '#15803d', padding: '4px 10px', borderRadius: '6px', fontSize: '11px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <Bot size={13} /> Delegated to FounderOS Agent
                    </span>
                  )}
                  {task.status === 'FAILED' && (
                    <span style={{ background: '#fee2e2', color: '#b91c1c', padding: '4px 10px', borderRadius: '6px', fontSize: '11px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <Bot size={13} /> Execution Failed
                    </span>
                  )}
                  {task.status === 'FAILED' && (
                    <button className="secondary-button" onClick={() => onDelegate(task.id)} style={{ height: '30px', fontSize: '12px', borderColor: '#fca5a5', color: '#b91c1c' }}>
                      <Bot size={14} /> Retry Agent
                    </button>
                  )}
                  {task.status !== 'COMPLETED' ? (
                    <button className="primary-button" onClick={() => onComplete(task.id)} style={{ height: '30px', fontSize: '12px' }}>
                      <Check size={14} /> Complete
                    </button>
                  ) : (
                    <span style={{ color: '#16a34a', fontSize: '12px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <CheckCircle2 size={14} /> Completed
                    </span>
                  )}
                </div>
              </div>

              <h3 style={{ margin: '14px 0 6px', fontSize: '16px', color: '#0f172a', fontWeight: 600 }}>{task.title}</h3>
              {task.description && <p style={{ margin: 0, color: '#334155', fontSize: '13px', lineHeight: '1.5' }}>{task.description}</p>}

              {task.agent_note && (
                <div style={{ marginTop: '12px', background: task.status === 'FAILED' ? '#fef2f2' : '#f8fafc', padding: '10px 12px', borderRadius: '8px', border: `1px solid ${task.status === 'FAILED' ? '#fca5a5' : '#e2e8f0'}`, color: task.status === 'FAILED' ? '#991b1b' : '#475569', fontSize: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Sparkles size={14} style={{ color: task.status === 'FAILED' ? '#ef4444' : '#2563eb', flex: '0 0 auto' }} />
                  <span><strong>{task.status === 'FAILED' ? 'Agent Error:' : 'Agent Synthesis:'}</strong> {task.agent_note}</span>
                </div>
              )}
            </article>
          )
        })
      )}
    </div>
  </div>
}

function NewTaskModal({ onClose, onSave }: { onClose: () => void; onSave: (task: any) => void }) {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [priority, setPriority] = useState('P1_HIGH')
  const [category, setCategory] = useState('TODAY')
  const [dueDate, setDueDate] = useState('Today')

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [onClose])

  return <div className="modal-backdrop" role="presentation" onClick={(e) => e.target === e.currentTarget && onClose()}>
    <section className="editor-modal" role="dialog" aria-modal="true" style={{ maxWidth: '560px' }}>
      <div className="modal-header">
        <div>
          <p className="eyebrow"><ListTodo size={14} /> FOUNDER WORKFLOW</p>
          <h2>Record New Founder Task</h2>
        </div>
        <button className="icon-button" onClick={onClose}><X size={18} /></button>
      </div>
      <p className="modal-copy">Add an urgent founder task or delegate it directly to FounderOS.</p>

      <div className="form-grid single editor-fields" style={{ margin: '16px 0' }}>
        <label className="field">
          <span>Task Title</span>
          <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="e.g. Review legal terms for enterprise contract" />
        </label>
        <label className="field">
          <span>Description / Details</span>
          <input value={description} onChange={(e) => setDescription(e.target.value)} placeholder="e.g. Atlas Logistics requires uptime SLA confirmation" />
        </label>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '10px' }}>
          <label className="field">
            <span>Priority</span>
            <select value={priority} onChange={(e) => setPriority(e.target.value)} style={{ width: '100%', height: '40px', borderRadius: '8px', border: '1px solid #e2e8f0', padding: '0 10px', fontSize: '13px' }}>
              <option value="P0_CRITICAL">P0 Critical</option>
              <option value="P1_HIGH">P1 High</option>
              <option value="P2_MEDIUM">P2 Medium</option>
              <option value="P3_LOW">P3 Low</option>
            </select>
          </label>
          <label className="field">
            <span>Category</span>
            <select value={category} onChange={(e) => setCategory(e.target.value)} style={{ width: '100%', height: '40px', borderRadius: '8px', border: '1px solid #e2e8f0', padding: '0 10px', fontSize: '13px' }}>
              <option value="TODAY">Today</option>
              <option value="UPCOMING">Upcoming</option>
              <option value="DELEGATED">Delegated</option>
            </select>
          </label>
          <label className="field">
            <span>Due Date</span>
            <input value={dueDate} onChange={(e) => setDueDate(e.target.value)} placeholder="e.g. Today 5:00 PM" />
          </label>
        </div>
      </div>

      <div className="modal-footer">
        <button className="secondary-button" onClick={onClose}>Cancel</button>
        <button className="primary-button" onClick={() => title && onSave({ title, description, priority, category, dueDate })}>
          Save Task <Check size={15} />
        </button>
      </div>
    </section>
  </div>
}

export default App
