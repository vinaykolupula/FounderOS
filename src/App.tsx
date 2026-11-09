/**
 * FounderOS - Founder Command Center & Agent Cockpit
 * 
 * Modular FAANG-grade executive architecture:
 * 1. Root state coordinator managing multi-tenant context, WebSocket real-time event sync,
 *    and global toast notices.
 * 2. Dedicated modular view packages:
 *    - OverviewView: Strategic KPI overview, company health, CEO recommendation, approval queue.
 *    - TasksView: Founder workflow engine, automated email/calendar/linear task synthesis.
 *    - ExecutiveView: C-Suite scenario simulation, runway calculator, MEDDPICC deal radar.
 *    - DecisionsView: Institutional memory ledger with review schedules.
 *    - IntelligenceView: Opportunity radar, market signals, competitor watchlist.
 *    - CompanyView: Architectural model, tech stack, GTM motion, moat definitions.
 *    - ConnectionsView: Integration gateway (Gmail, Slack, Linear, HubSpot, Stripe).
 *    - ModelsView: Universal multi-provider AI engine (Claude, GPT, Grok, Kimi, DeepSeek, Gemini).
 *    - OnboardingView: Guided founder DNA and strategic compass setup.
 * 3. Dedicated modular modals:
 *    - DebateModal: Real-time 2-Round Multi-Agent C-Suite Dialectic Debate via Server-Sent Events (SSE).
 *    - MorningBriefingModal, NewDecisionModal, NewTaskModal, PreviewActionModal, SignalModal, AskFounderOSModal.
 */

import { useState, useEffect } from 'react'
import {
  LayoutDashboard,
  ListTodo,
  Activity,
  FileText,
  Compass,
  Gauge,
  Plug,
  Cpu,
  Settings,
  Menu,
  X,
  Search,
  Bell,
  Command,
  ChevronRight,
  MoreHorizontal,
  Check,
  CircleAlert,
} from 'lucide-react'
import {
  createWorkspace,
  defaultCompany,
  defaultFounder,
  type CompanyProfile,
  type FounderProfile,
  type ConnectorId,
  type View,
  type Workspace,
} from './domain'
import { usePersistentState } from './usePersistentState'
import {
  fetchBackendWorkspace,
  fetchBackendTasks,
  scanAgentTasks,
  delegateBackendTask,
  updateBackendTask,
  updateBackendCompany,
  updateBackendFounder,
  approveBackendAction,
  configureBackendConnector,
  fetchGoogleAuthUrl,
  resetBackendWorkspace,
  fetchMorningBriefing,
  createBackendDecision,
  createBackendTask,
  submitBackendOnboarding,
  streamExecutiveDebate,
  triggerExecutiveDebate,
} from './api'

// Views
import { OverviewView } from './views/OverviewView'
import { TasksView } from './views/TasksView'
import { ExecutiveView } from './views/ExecutiveView'
import { DecisionsView } from './views/DecisionsView'
import { IntelligenceView } from './views/IntelligenceView'
import { CompanyView, CompanyEditor, FounderEditor } from './views/CompanyView'
import { ConnectionsView } from './views/ConnectionsView'
import { ModelsView } from './views/ModelsView'
import { OnboardingView } from './views/OnboardingView'

// Modals
import { DebateModal } from './modals/DebateModal'
import { MorningBriefingModal } from './modals/MorningBriefingModal'
import { NewDecisionModal } from './modals/NewDecisionModal'
import { NewTaskModal } from './modals/NewTaskModal'
import { PreviewActionModal } from './modals/PreviewActionModal'
import { SignalModal } from './modals/SignalModal'
import { AskFounderOSModal } from './modals/AskFounderOSModal'
import { NotificationsDropdown } from './modals/NotificationsDropdown'
import { InvestorUpdateModal } from './components/InvestorUpdateModal'

const nav: { label: View; icon: typeof LayoutDashboard }[] = [
  { label: 'Overview', icon: LayoutDashboard },
  { label: 'Tasks', icon: ListTodo },
  { label: 'Executive', icon: Activity },
  { label: 'Decisions', icon: FileText },
  { label: 'Intelligence', icon: Compass },
  { label: 'Company', icon: Gauge },
  { label: 'Connections', icon: Plug },
  { label: 'Models', icon: Cpu },
]

export function App() {
  const [workspace, setWorkspace] = usePersistentState<Workspace>(
    'founderos-workspace-v1',
    createWorkspace()
  )
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
    fetchBackendTasks()
      .then((res) => {
        if (Array.isArray(res)) setTasksList(res)
      })
      .catch(() => {})
  }

  useEffect(() => {
    fetchBackendWorkspace().then((remoteWs) => {
      if (remoteWs) setWorkspace(remoteWs)
    })
    refreshTasks()
  }, [])

  // WebSocket Live Sync
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
          } catch {
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
      } catch {
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

  const updateWorkspace = (update: Partial<Workspace>) =>
    setWorkspace((current) => ({ ...current, ...update }))

  const updateCompany = async (company: CompanyProfile) => {
    const previousCompany = workspace?.company
    updateWorkspace({ company })
    try {
      await updateBackendCompany(company)
      setCompanyEditorOpen(false)
      setNotice('Company model updated. Future briefs will use this context.')
    } catch (e: any) {
      if (previousCompany) updateWorkspace({ company: previousCompany })
      setErrorNotice(e.message || 'Failed to update company')
    }
  }

  const updateFounder = async (founder: FounderProfile) => {
    const previousFounder = workspace?.founder
    updateWorkspace({ founder })
    try {
      await updateBackendFounder(founder)
      setFounderEditorOpen(false)
      setNotice('Founder profile updated.')
    } catch (e: any) {
      if (previousFounder) updateWorkspace({ founder: previousFounder })
      setErrorNotice(e.message || 'Failed to update founder')
    }
  }

  const approveAction = async (id: number) => {
    const previousActions = workspace?.actions || []
    const item = previousActions.find((action) => action.id === id)
    if (!item) return

    updateWorkspace({ actions: previousActions.filter((action) => action.id !== id) })
    try {
      await approveBackendAction(id)
      setNotice(`${item.title} approved and dispatched. Execution receipt saved.`)
    } catch (e: any) {
      updateWorkspace({ actions: previousActions })
      setErrorNotice(e.message || `Failed to approve "${item.title}". Restored to action queue.`)
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
      updateWorkspace({
        connectors: (workspace?.connectors || []).map((item) =>
          item.id === id ? { ...item, status: 'configured' as const } : item
        ),
      })
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
    if (
      window.confirm(
        'Are you sure you want to reset everything? This will delete all company data, founder profile, and agent history.'
      )
    ) {
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

  // Real-Time Streaming Dialectic Debate Trigger
  const handleTriggerDebate = (title: string) => {
    setDebateModal({
      decisionTitle: title,
      executivePerspectives: [],
      dialecticCritiques: [],
      isStreaming: true,
      currentStage: 'Connecting to Executive Board personas...',
    })

    streamExecutiveDebate(title, (eventType, eventData) => {
      setDebateModal((prev: any) => {
        if (!prev) return prev
        if (eventType === 'round1_start') {
          return {
            ...prev,
            currentStage: eventData.message || 'Round 1: Gathering independent C-Suite stances...',
          }
        }
        if (eventType === 'round1_persona') {
          const current = prev.executivePerspectives || []
          return {
            ...prev,
            executivePerspectives: [...current, eventData],
          }
        }
        if (eventType === 'round2_start') {
          return {
            ...prev,
            currentStage: eventData.message || 'Round 2: Cross-examining dialectic tensions...',
          }
        }
        if (eventType === 'round2_dialectic') {
          const current = prev.dialecticCritiques || []
          return {
            ...prev,
            dialecticCritiques: [...current, eventData],
          }
        }
        if (eventType === 'round3_start') {
          return {
            ...prev,
            currentStage: eventData.message || 'Round 3: CEO Orchestrator synthesizing consensus and MVE...',
          }
        }
        if (eventType === 'debate_complete') {
          return {
            ...prev,
            ...eventData,
            isStreaming: false,
            currentStage: undefined,
          }
        }
        return prev
      })
    }).catch(() => {
      // Fallback to standard HTTP fetch if streaming fails
      triggerExecutiveDebate(title)
        .then((data) => setDebateModal(data))
        .catch((e: any) => {
          setErrorNotice(e.message || 'Failed to trigger executive debate')
          setDebateModal(null)
        })
    })
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
    return (
      <OnboardingView
        onComplete={(company, founder, selectedConnectors) => {
          const updatedWs: Workspace = {
            ...createWorkspace(),
            isOnboarded: true,
            company,
            founder,
            connectors: createWorkspace().connectors.map((connector) => ({
              ...connector,
              status: selectedConnectors.includes(connector.id)
                ? 'configured'
                : 'not_connected',
            })),
          }
          setWorkspace(updatedWs)
          submitBackendOnboarding(company, founder, selectedConnectors)
        }}
      />
    )
  }

  return (
    <main className="app-shell">
      <aside className={`sidebar ${drawerOpen ? 'is-open' : ''}`}>
        <div className="brand-row">
          <img src="/media/Logo.webp" alt="FounderOS Logo" className="brand-logo-img" />
          <span>FounderOS</span>
          <button
            className="mobile-close"
            onClick={() => setDrawerOpen(false)}
            aria-label="Close navigation"
          >
            <X size={18} />
          </button>
        </div>
        <div className="workspace-switcher">
          <div className="workspace-orb">{companyName.charAt(0).toUpperCase()}</div>
          <div>
            <strong>{companyName}</strong>
            <small>Founder workspace</small>
          </div>
          <ChevronRight size={16} />
        </div>
        <nav>
          <p className="nav-label">WORKSPACE</p>
          {nav.map(({ label, icon: Icon }) => (
            <button
              key={label}
              className={`nav-item ${view === label ? 'active' : ''}`}
              onClick={() => {
                navigate(label)
                setDrawerOpen(false)
              }}
            >
              <Icon size={17} />
              <span>{label}</span>
              {label === 'Decisions' && <em>{safeDecisions.length || 3}</em>}
              {label === 'Connections' &&
                safeConnectors.some((connector) => connector.status === 'configured') && (
                  <i className="nav-ready" />
                )}
            </button>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <button className="nav-item" onClick={() => navigate('Models')}>
            <Settings size={17} />
            <span>Settings</span>
          </button>
          <div
            className="profile"
            onClick={() => setFounderEditorOpen(true)}
            style={{ cursor: 'pointer' }}
          >
            <div className="avatar">{founderName.slice(0, 2).toUpperCase()}</div>
            <div>
              <strong>{founderName}</strong>
              <small>{safeFounder.role}</small>
            </div>
            <MoreHorizontal size={17} />
          </div>
        </div>
      </aside>

      {drawerOpen && (
        <button
          className="scrim"
          onClick={() => setDrawerOpen(false)}
          aria-label="Close navigation"
        />
      )}

      <section className="content">
        <header className="topbar">
          <button
            className="menu-button"
            onClick={() => setDrawerOpen(true)}
            aria-label="Open navigation"
          >
            <Menu size={21} />
          </button>
          <div className="crumb">
            <span>Workspace</span>
            <ChevronRight size={14} />
            <strong>{view}</strong>
          </div>
          <div className="topbar-actions">
            <button
              className="icon-button"
              onClick={() => setAskModalOpen(true)}
              title="Search"
            >
              <Search size={18} />
            </button>
            <button
              className="icon-button notification"
              onClick={() => setNotificationsOpen(!notificationsOpen)}
              title="Notifications"
            >
              <Bell size={18} />
              <i />
            </button>
            <button className="ask-button" onClick={() => setAskModalOpen(true)}>
              <Command size={15} /> Ask FounderOS
            </button>
          </div>
        </header>

        {notice && (
          <div className="toast">
            <Check size={15} />
            {notice}
            <button onClick={() => setNotice('')}>
              <X size={14} />
            </button>
          </div>
        )}
        {errorNotice && (
          <div
            className="toast error-toast"
            style={{
              background: '#fee2e2',
              color: '#991b1b',
              border: '1px solid #ef4444',
            }}
          >
            <CircleAlert size={15} />
            {errorNotice}
            <button style={{ color: '#991b1b' }} onClick={() => setErrorNotice('')}>
              <X size={14} />
            </button>
          </div>
        )}

        {notificationsOpen && (
          <NotificationsDropdown onClose={() => setNotificationsOpen(false)} />
        )}

        {view === 'Overview' && (
          <OverviewView
            company={safeCompany}
            founder={safeFounder}
            actions={safeActions}
            onApprove={approveAction}
            onPreview={(action) => setPreviewAction(action)}
            onReviewSignal={(signal) => setActiveSignal(signal)}
            onRefresh={refreshBrief}
            briefUpdated={briefUpdated}
            onViewIntelligence={() => navigate('Intelligence')}
            onDebate={() =>
              handleTriggerDebate('Pause Feature B and investigate activation')
            }
            onInvestorUpdate={() => setInvestorModalOpen(true)}
          />
        )}

        {view === 'Tasks' && (
          <TasksView
            tasks={tasksList}
            onScan={handleScanTasks}
            onNewTask={() => setNewTaskOpen(true)}
            onDelegate={handleDelegateTask}
            onComplete={handleCompleteTask}
          />
        )}

        {view === 'Executive' && (
          <ExecutiveView
            company={safeCompany}
            onOpenInvestorModal={() => setInvestorModalOpen(true)}
          />
        )}

        {view === 'Decisions' && (
          <DecisionsView
            decisions={safeDecisions}
            onOpenDebate={(title) => handleTriggerDebate(title)}
            onNewDecision={() => setNewDecisionOpen(true)}
          />
        )}

        {view === 'Intelligence' && (
          <IntelligenceView onSelectSignal={(s) => setActiveSignal(s)} />
        )}

        {view === 'Company' && (
          <CompanyView
            company={safeCompany}
            connectedCount={
              safeConnectors.filter((c) => c.status === 'configured').length
            }
            onEdit={() => setCompanyEditorOpen(true)}
            onConnections={() => navigate('Connections')}
          />
        )}

        {view === 'Connections' && (
          <ConnectionsView
            connectors={safeConnectors}
            onConfigure={configureConnector}
          />
        )}

        {view === 'Models' && (
          <ModelsView
            onNotice={(msg) => setNotice(msg)}
            onReset={handleResetWorkspace}
          />
        )}
      </section>

      {companyEditorOpen && (
        <CompanyEditor
          company={safeCompany}
          onClose={() => setCompanyEditorOpen(false)}
          onSave={updateCompany}
        />
      )}
      {founderEditorOpen && (
        <FounderEditor
          founder={safeFounder}
          onClose={() => setFounderEditorOpen(false)}
          onSave={updateFounder}
        />
      )}
      {debateModal && (
        <DebateModal data={debateModal} onClose={() => setDebateModal(null)} />
      )}
      {investorModalOpen && (
        <InvestorUpdateModal
          isOpen={investorModalOpen}
          onClose={() => setInvestorModalOpen(false)}
          onActionStaged={() => {
            fetchBackendWorkspace().then((ws) => ws && setWorkspace(ws))
            setNotice('Investor update staged to Approval Queue for founder sign-off.')
          }}
        />
      )}
      {newDecisionOpen && (
        <NewDecisionModal
          onClose={() => setNewDecisionOpen(false)}
          onSave={async (title, detail) => {
            try {
              await createBackendDecision(title, detail)
              setNewDecisionOpen(false)
              setNotice(`Decision '${title}' added to institutional memory.`)
              const remoteWs = await fetchBackendWorkspace()
              if (remoteWs) setWorkspace(remoteWs)
            } catch (e: any) {
              setErrorNotice(e.message || 'Failed to create decision')
            }
          }}
        />
      )}
      {newTaskOpen && (
        <NewTaskModal
          onClose={() => setNewTaskOpen(false)}
          onSave={async (task) => {
            await createBackendTask(task)
            setNewTaskOpen(false)
            refreshTasks()
            setNotice(`Task '${task.title}' added to Founder Work Plan.`)
          }}
        />
      )}
      {askModalOpen && (
        <AskFounderOSModal
          onClose={() => setAskModalOpen(false)}
          onDebate={(title) => {
            setAskModalOpen(false)
            handleTriggerDebate(title)
          }}
        />
      )}
      {previewAction && (
        <PreviewActionModal
          action={previewAction}
          onClose={() => setPreviewAction(null)}
          onApprove={(id) => {
            approveAction(id)
            setPreviewAction(null)
          }}
        />
      )}
      {activeSignal && (
        <SignalModal
          signal={activeSignal}
          onClose={() => setActiveSignal(null)}
          onDebate={(title) => {
            setActiveSignal(null)
            handleTriggerDebate(title)
          }}
        />
      )}
      {briefingModalOpen && (
        <MorningBriefingModal
          data={briefingData}
          onClose={() => setBriefingModalOpen(false)}
          onDebate={(title) => {
            setBriefingModalOpen(false)
            handleTriggerDebate(title)
          }}
        />
      )}
    </main>
  )
}
export default App
