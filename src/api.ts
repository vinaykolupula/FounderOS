/**
 * FounderOS Frontend API Client & Request Adapter
 * 
 * Provides typed methods for interacting with the FastAPI backend REST API.
 * Features:
 * - Automatic timeout handling (8s default) via AbortController.
 * - JSON error extraction throwing descriptive Error objects for global UI toast handling.
 * - Full domain model deserialization and fallback mapping.
 */

import { type CompanyProfile, type FounderProfile, type ConnectorId, type Workspace } from './domain'

const API_BASE = (import.meta as any).env?.VITE_API_BASE || 'http://127.0.0.1:8000/api'
const DEFAULT_TIMEOUT_MS = 15000 // 15s for standard CRUD
const AI_TIMEOUT_MS = 60000 // 60s for multi-agent LLM reasoning

/**
 * Helper to retrieve client-stored auth credentials for multi-tenant requests.
 */
function getAuthHeaders(): Record<string, string> {
  const headers: Record<string, string> = {}
  const jwt = localStorage.getItem('founderos_jwt_token')
  if (jwt) {
    headers['Authorization'] = `Bearer ${jwt}`
  }
  const token = localStorage.getItem('founderos_api_key')
  if (token) {
    headers['X-FounderOS-Key'] = token
  }
  return headers
}

/**
 * Utility wrapper around `fetch` adding an automatic abort timeout and auth headers.
 */
async function fetchWithTimeout(
  url: string,
  options: RequestInit = {},
  timeoutMs: number = DEFAULT_TIMEOUT_MS
): Promise<Response> {
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs)
  try {
    const authHeaders = getAuthHeaders()
    const mergedHeaders = {
      ...authHeaders,
      ...(options.headers || {}),
    }
    const res = await fetch(url, {
      ...options,
      headers: mergedHeaders,
      signal: controller.signal,
    })
    return res
  } finally {
    clearTimeout(timeoutId)
  }
}

/**
 * Fetches the root workspace context (Company Profile, Founder Profile, Connectors, Actions, Decisions).
 */
export async function fetchBackendWorkspace(): Promise<Workspace | null> {
  try {
    const res = await fetchWithTimeout(`${API_BASE}/workspace`, { method: 'GET' })
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}))
      throw new Error(errData.detail || 'Failed to fetch workspace context')
    }
    const data = await res.json()
    if (!data || !data.company) return null

    return {
      id: data.id,
      isOnboarded: data.isOnboarded,
      company: {
        name: data.company.name || 'FounderOS',
        websiteUrl: data.company.websiteUrl || '',
        linkedinUrl: data.company.linkedinUrl || '',
        socialUrl: data.company.socialUrl || '',
        businessModel: data.company.businessModel || 'B2B SaaS',
        platformFocus: data.company.platformFocus || 'Web Application',
        fundingState: data.company.fundingState || 'Bootstrapped',
        revenueRange: data.company.revenueRange || '$10k-$100k MRR',
        stage: data.company.stage || 'Early revenue',
        teamSize: data.company.teamSize || '2-5 people',
        idealCustomer: data.company.idealCustomer || 'Mid-market logistics teams',
        objective: data.company.objective || 'Reach $60k MRR with sustainable activation',
        primaryMetric: data.company.primaryMetric || 'Weekly activated accounts',
        primaryConstraint: data.company.primaryConstraint || 'First-value completion',
        runwayMonths: data.company.runwayMonths || 12,
        burnRate: data.company.burnRate || 'Unknown',
        gtmMotion: data.company.gtmMotion || 'Product-Led Growth',
        techStack: data.company.techStack || 'React, Node.js, Postgres',
        competitiveMoat: data.company.competitiveMoat || 'First mover advantage',
      },
      founder: data.founder ? {
        name: data.founder.name || '',
        role: data.founder.role || 'Solo Founder',
        background: data.founder.background || 'Engineering / Technical',
        experienceLevel: data.founder.experienceLevel || 'First-time Founder',
        domainExpertise: data.founder.domainExpertise || '',
        superpower: data.founder.superpower || 'Building & Engineering',
        primaryGap: data.founder.primaryGap || 'Sales & Closing Deals',
        learningFocus: data.founder.learningFocus || '',
        communicationStyle: data.founder.communicationStyle || 'Direct and brief',
        energyState: data.founder.energyState || 'Steady pace',
        coreValues: data.founder.coreValues || 'Speed, Customer Obsession',
      } : {
        name: '',
        role: 'Solo Founder',
        background: 'Engineering / Technical',
        experienceLevel: 'First-time Founder',
        domainExpertise: '',
        superpower: 'Building & Engineering',
        primaryGap: 'Sales & Closing Deals',
        learningFocus: '',
        communicationStyle: 'Direct and brief',
        energyState: 'Steady pace',
        coreValues: 'Speed, Customer Obsession'
      },
      connectors: (data.connectors || []).map((c: any) => ({
        id: c.id,
        name: c.name,
        description: c.description,
        category: c.category,
        status: (c.status === 'configured' ? 'configured' : 'not_connected') as 'configured' | 'not_connected',
      })),
      actions: (data.actions || []).map((a: any) => ({
        id: a.id,
        title: a.title,
        detail: a.detail,
        source: a.source,
        status: a.status === 'Draft' ? 'Draft' : 'Ready',
      })),
      decisions: (data.decisions || []).map((d: any) => ({
        id: d.id,
        decisionCode: d.decisionCode,
        title: d.title,
        detail: d.detail,
        status: d.status,
      })),
    }
  } catch (err: any) {
    console.warn('FounderOS API fetch failed:', err)
    throw err
  }
}

/**
 * Submits first-run onboarding payload (Company, Founder DNA, Connectors) to backend.
 */
export async function submitBackendOnboarding(company: CompanyProfile, founder: FounderProfile, selectedConnectors: ConnectorId[]): Promise<boolean> {
  try {
    const res = await fetchWithTimeout(`${API_BASE}/onboarding`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ company, founder, selectedConnectors }),
    })
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}))
      throw new Error(errData.detail || 'Failed to complete onboarding')
    }
    return true
  } catch (err) {
    throw err
  }
}

/**
 * Purges workspace database state to reset application for a fresh start.
 */
export async function resetBackendWorkspace(): Promise<boolean> {
  try {
    const res = await fetchWithTimeout(`${API_BASE}/workspace`, {
      method: 'DELETE',
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || 'Request failed')
    }
    return true
  } catch (err) {
    throw err
  }
}

/**
 * Updates Company Profile architecture & financials in backend DB.
 */
export async function updateBackendCompany(company: CompanyProfile): Promise<boolean> {
  try {
    const res = await fetchWithTimeout(`${API_BASE}/company`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(company),
    })
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}))
      throw new Error(errData.detail || 'Failed to update company context')
    }
    return true
  } catch (err) {
    throw err
  }
}

/**
 * Updates Founder Profile DNA & Communication preferences in backend DB.
 */
export async function updateBackendFounder(founder: any): Promise<boolean> {
  try {
    const res = await fetchWithTimeout(`${API_BASE}/founder`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(founder)
    })
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}))
      throw new Error(errData.detail || 'Failed to update founder profile')
    }
    return true
  } catch (err) {
    throw err
  }
}

/**
 * Approves a drafted ActionItem in the action queue.
 */
export async function approveBackendAction(actionId: number): Promise<boolean> {
  try {
    const res = await fetchWithTimeout(`${API_BASE}/actions/${actionId}/approve`, {
      method: 'POST',
    })
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}))
      throw new Error(errData.detail || 'Failed to approve action')
    }
    return true
  } catch (err) {
    throw err
  }
}

/**
 * Configures an external system connector (e.g. Gmail, Slack, Linear).
 */
export async function configureBackendConnector(connectorId: ConnectorId): Promise<boolean> {
  try {
    const res = await fetchWithTimeout(`${API_BASE}/connectors/${connectorId}/configure`, {
      method: 'POST',
    })
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}))
      throw new Error(errData.detail || 'Failed to configure connector')
    }
    return true
  } catch (err) {
    throw err
  }
}

/**
 * Fetches Google Workspace OAuth authorization URL from backend.
 */
export async function fetchGoogleAuthUrl(): Promise<string | null> {
  try {
    const res = await fetchWithTimeout(`${API_BASE}/auth/google/login`, { method: 'GET' })
    if (!res.ok) return null
    const data = await res.json()
    return data.authUrl
  } catch {
    return null
  }
}

/**
 * Generates dynamic daily CEO brief using RAG vector evidence ranking.
 */
export async function generateDynamicBrief(): Promise<any> {
  try {
    const res = await fetchWithTimeout(`${API_BASE}/brief/generate`, { method: 'POST' }, AI_TIMEOUT_MS)
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || 'Request failed to generate CEO brief')
    }
    return await res.json()
  } catch (err) {
    throw err
  }
}

/**
 * Triggers Multi-Agent Executive Board debate (CRO, CFO, VP CS, Skeptic, CTO).
 */
export async function triggerExecutiveDebate(decisionTitle: string): Promise<any> {
  try {
    const res = await fetchWithTimeout(`${API_BASE}/debate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ decisionTitle }),
    }, AI_TIMEOUT_MS)
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || 'Failed to trigger executive debate')
    }
    return await res.json()
  } catch (err) {
    throw err
  }
}

/**
 * Streams Multi-Agent Executive Board debate in real-time via Server-Sent Events (SSE).
 */
export async function streamExecutiveDebate(
  decisionTitle: string,
  onEvent: (eventType: string, data: any) => void,
  signal?: AbortSignal
): Promise<any> {
  const url = `${API_BASE}/debate/stream?decisionTitle=${encodeURIComponent(decisionTitle)}`
  const headers = getAuthHeaders()

  const response = await fetch(url, {
    method: 'GET',
    headers: {
      ...headers,
      'Accept': 'text/event-stream',
    },
    signal,
  })

  if (!response.ok) {
    const err = await response.json().catch(() => ({}))
    throw new Error(err.detail || 'Failed to initiate executive debate stream')
  }

  const reader = response.body?.getReader()
  if (!reader) {
    throw new Error('Streaming response body not available')
  }

  const decoder = new TextDecoder()
  let buffer = ''
  let finalResult: any = null

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n\n')
    buffer = lines.pop() || ''

    for (const chunk of lines) {
      if (!chunk.trim()) continue
      let eventType = 'message'
      let dataStr = ''

      const chunkLines = chunk.split('\n')
      for (const line of chunkLines) {
        if (line.startsWith('event:')) {
          eventType = line.slice(6).trim()
        } else if (line.startsWith('data:')) {
          dataStr = line.slice(5).trim()
        }
      }

      if (dataStr) {
        try {
          const parsedData = JSON.parse(dataStr)
          if (eventType === 'debate_complete') {
            finalResult = parsedData
          }
          onEvent(eventType, parsedData)
        } catch (e) {
          console.warn('Failed to parse SSE data chunk:', dataStr)
        }
      }
    }
  }

  return finalResult
}

/**
 * Creates a new decision entry in the institutional decision ledger.
 */
export async function createBackendDecision(title: string, detail: string): Promise<boolean> {
  try {
    const res = await fetchWithTimeout(`${API_BASE}/decisions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, detail, status: 'Open' }),
    })
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}))
      throw new Error(errData.detail || 'Failed to create decision')
    }
    return true
  } catch (err) {
    throw err
  }
}

/**
 * Fetches configured AI Provider model settings and active status.
 */
export async function fetchModelSettings(): Promise<any> {
  try {
    const res = await fetchWithTimeout(`${API_BASE}/settings/models`, { method: 'GET' })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || 'Failed to fetch AI model settings')
    }
    return await res.json()
  } catch (err) {
    throw err
  }
}

/**
 * Saves AI Provider selection, custom base URL, cognitive depth reasoning effort, and Vault-encrypted API key.
 */
export async function saveModelSetting(
  providerName: string,
  selectedModel: string,
  apiKey: string,
  isActive: boolean,
  customBaseUrl?: string,
  reasoningEffort?: string
): Promise<boolean> {
  try {
    const res = await fetchWithTimeout(`${API_BASE}/settings/models`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ providerName, selectedModel, apiKey, isActive, customBaseUrl, reasoningEffort }),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || 'Failed to save AI model setting')
    }
    return true
  } catch (err) {
    throw err
  }
}

/**
 * Tests live connection health & latency to an AI Provider.
 */
export async function testModelConnection(
  providerName: string,
  selectedModel: string,
  apiKey: string,
  customBaseUrl?: string,
  reasoningEffort?: string
): Promise<any> {
  try {
    const res = await fetchWithTimeout(`${API_BASE}/settings/models/test`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ providerName, selectedModel, apiKey, customBaseUrl, reasoningEffort }),
    }, AI_TIMEOUT_MS)
    if (!res.ok) return { success: false, status: 'Server Error' }
    return await res.json()
  } catch {
    return { success: false, status: 'Connection Timeout' }
  }
}

/**
 * Dynamically queries provider's live /v1/models endpoint to fetch active models.
 */
export async function discoverProviderModels(
  providerName: string,
  apiKey?: string,
  customBaseUrl?: string
): Promise<{ provider: string; models: string[]; count: number }> {
  try {
    const res = await fetchWithTimeout(`${API_BASE}/settings/models/discover`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ providerName, apiKey, customBaseUrl }),
    }, AI_TIMEOUT_MS)
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || 'Failed to discover models')
    }
    return await res.json()
  } catch (err) {
    throw err
  }
}

/**
 * Fetches task list prioritized by urgency.
 */
export async function fetchBackendTasks(): Promise<any[]> {
  try {
    const res = await fetchWithTimeout(`${API_BASE}/tasks`, { method: 'GET' })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || 'Failed to fetch tasks')
    }
    return await res.json()
  } catch (err) {
    throw err
  }
}

/**
 * Creates a manual founder task.
 */
export async function createBackendTask(task: { title: string; description?: string; priority?: string; category?: string; source?: string; dueDate?: string }): Promise<any> {
  try {
    const res = await fetchWithTimeout(`${API_BASE}/tasks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: task.title,
        description: task.description || '',
        priority: task.priority || 'P1_HIGH',
        category: task.category || 'TODAY',
        source: task.source || 'FOUNDER_MANUAL',
        due_date: task.dueDate || 'Today'
      }),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || 'Failed to create task')
    }
    return await res.json()
  } catch (err) {
    throw err
  }
}

/**
 * Updates task status or attributes.
 */
export async function updateBackendTask(taskId: number, payload: any): Promise<boolean> {
  try {
    const res = await fetchWithTimeout(`${API_BASE}/tasks/${taskId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || 'Failed to update task')
    }
    return true
  } catch (err) {
    throw err
  }
}

/**
 * Delegates a task to the autonomous AI worker for processing.
 */
export async function delegateBackendTask(taskId: number): Promise<any> {
  try {
    const res = await fetchWithTimeout(`${API_BASE}/tasks/${taskId}/delegate`, { method: 'POST' }, AI_TIMEOUT_MS)
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || 'Failed to delegate task')
    }
    return await res.json()
  } catch (err) {
    throw err
  }
}

/**
 * Triggers automated system scan of connected tools (Gmail, Calendar, Linear).
 */
export async function scanAgentTasks(): Promise<any[]> {
  try {
    const res = await fetchWithTimeout(`${API_BASE}/tasks/scan`, { method: 'POST' }, AI_TIMEOUT_MS)
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || 'Failed to scan agent tasks')
    }
    return await res.json()
  } catch (err) {
    throw err
  }
}

/**
 * Fetches the daily CEO Executive Morning Briefing.
 */
export async function fetchMorningBriefing(): Promise<any> {
  try {
    const res = await fetchWithTimeout(`${API_BASE}/briefing`, {}, AI_TIMEOUT_MS)
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || 'Failed to fetch morning briefing')
    }
    return await res.json()
  } catch (err) {
    throw err
  }
}

// ==========================================
// C-Suite Daily Executive Operating Tools APIs
// ==========================================

export async function generateInvestorUpdate(payload: {
  monthYear?: string
  customHighlights?: string[]
  customLowlights?: string[]
  customAsks?: string[]
}): Promise<any> {
  const res = await fetchWithTimeout(`${API_BASE}/executive-tools/investor-update/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  }, AI_TIMEOUT_MS)
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || 'Failed to generate investor update')
  }
  return await res.json()
}

export async function stageInvestorUpdateAction(payload: {
  subjectLine: string
  fullMarkdown: string
}): Promise<any> {
  const res = await fetchWithTimeout(`${API_BASE}/executive-tools/investor-update/stage-action`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || 'Failed to stage investor update')
  }
  return await res.json()
}

export async function classifyTasksLNO(tasks: any[]): Promise<any> {
  const res = await fetchWithTimeout(`${API_BASE}/executive-tools/tasks/classify-lno`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ tasks })
  }, AI_TIMEOUT_MS)
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || 'Failed to classify tasks')
  }
  return await res.json()
}

export async function calculateRunwayAnalysis(payload: {
  cashBalance: number
  monthlyBurn: number
  monthlyRevenue: number
  momGrowthRate?: number
}): Promise<any> {
  const res = await fetchWithTimeout(`${API_BASE}/executive-tools/finance/runway-analysis`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || 'Failed to calculate runway')
  }
  return await res.json()
}

export async function simulateFinancialScenario(payload: {
  cashBalance: number
  monthlyBurn: number
  monthlyRevenue: number
  momGrowthRate: number
  headcountDelta: number
  avgAnnualSalary: number
  revGrowthDeltaPct: number
  monthlyToolingSpendDelta: number
}): Promise<any> {
  const res = await fetchWithTimeout(`${API_BASE}/executive-tools/finance/simulate-scenario`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || 'Failed to simulate scenario')
  }
  return await res.json()
}

export async function runPreMortemAnalysis(payload: {
  proposalTitle: string
  technicalScope: string
  techStack?: string
  primaryConstraint?: string
}): Promise<any> {
  const res = await fetchWithTimeout(`${API_BASE}/executive-tools/technical/pre-mortem`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  }, AI_TIMEOUT_MS)
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || 'Failed to run pre-mortem analysis')
  }
  return await res.json()
}

export async function generateArchitectureRecord(payload: {
  title: string
  contextProblem: string
  optionsConsidered: string[]
  chosenSolution: string
  techStack?: string
}): Promise<any> {
  const res = await fetchWithTimeout(`${API_BASE}/executive-tools/technical/adr`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  }, AI_TIMEOUT_MS)
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || 'Failed to generate ADR')
  }
  return await res.json()
}

export async function auditMeddpiccDeal(payload: {
  metricsDefined: boolean
  hasEconomicBuyer: boolean
  decisionCriteriaKnown: boolean
  decisionProcessMapped: boolean
  paperProcessMapped: boolean
  painImplicated: boolean
  hasChampion: boolean
  competitionIdentified: boolean
}): Promise<any> {
  const res = await fetchWithTimeout(`${API_BASE}/executive-tools/sales/meddpicc-audit`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || 'Failed to audit deal')
  }
  return await res.json()
}

export async function coachSalesObjection(payload: {
  objection: string
  prospectRole?: string
  productValueProp?: string
}): Promise<any> {
  const res = await fetchWithTimeout(`${API_BASE}/executive-tools/sales/objection-coach`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  }, AI_TIMEOUT_MS)
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || 'Failed to generate objection coach talk track')
  }
  return await res.json()
}

export async function calculatePmfScore(payload: {
  veryDisappointedCount: number
  somewhatDisappointedCount: number
  notDisappointedCount: number
}): Promise<any> {
  const res = await fetchWithTimeout(`${API_BASE}/executive-tools/product/pmf-score`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || 'Failed to calculate PMF score')
  }
  return await res.json()
}

export async function analyzePmfFeedback(feedbackItems: Array<{ sentiment: string; userRole: string; mainBenefit: string; wish: string }>): Promise<any> {
  const res = await fetchWithTimeout(`${API_BASE}/executive-tools/product/pmf-analysis`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ feedbackItems })
  }, AI_TIMEOUT_MS)
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || 'Failed to analyze PMF feedback')
  }
  return await res.json()
}

export interface ObservabilityUsageData {
  totalCostUsd: number
  totalTokens: number
  totalInferences: number
  avgLatencyMs: number
  providerBreakdown: Record<string, {
    calls: number
    promptTokens: number
    completionTokens: number
    totalTokens: number
    costUsd: number
  }>
}

export async function fetchObservabilityUsage(days: number = 30): Promise<ObservabilityUsageData> {
  const res = await fetchWithTimeout(`${API_BASE}/observability/usage?days=${days}`)
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || 'Failed to fetch AI observability metrics')
  }
  return await res.json()
}

export async function fetchRecentObservabilityLogs(limit: number = 20): Promise<any[]> {
  const res = await fetchWithTimeout(`${API_BASE}/observability/recent?limit=${limit}`)
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || 'Failed to fetch AI telemetry logs')
  }
  return await res.json()
}

