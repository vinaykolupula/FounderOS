import { useState, useEffect } from 'react'
import {
  ShieldCheck,
  CheckCircle2,
  CircleDot,
  Cpu,
  Sparkles,
  Eye,
  EyeOff,
  Check,
  Flame,
  Activity,
  DollarSign,
  Layers,
  Timer,
} from 'lucide-react'
import {
  fetchModelSettings,
  saveModelSetting,
  testModelConnection,
  discoverProviderModels,
  fetchObservabilityUsage,
  type ObservabilityUsageData,
} from '../api'

export function ModelsView({
  onNotice,
  onReset,
}: {
  onNotice: (msg: string) => void
  onReset: () => void
}) {
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
  const [observabilityData, setObservabilityData] = useState<ObservabilityUsageData | null>(null)

  const loadData = () => {
    fetchObservabilityUsage()
      .then((res) => setObservabilityData(res))
      .catch(() => {})

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

  const availableModelList =
    discoveredModels.length > 0
      ? discoveredModels
      : currentProviderInfo?.availableModels || [selectedModel]

  return (
    <div className="page simple-page">
      <div className="simple-heading">
        <div>
          <p className="eyebrow">AI REASONING LAYER & UNIVERSAL CONNECTORS</p>
          <h1>Frontier Models & AI Connectors</h1>
          <p className="subhead">
            Hermes & OpenClaw style dynamic provider protocol. Connect Claude Opus/Fable 5, GPT-5.6 Sol/Luna, Grok 4.6, Kimi K3, Gemini 3.7, DeepSeek V4 Pro, GLM-5.2, or Nemotron 3 Ultra.
          </p>
        </div>
        <span className="approval-note">
          <ShieldCheck size={15} /> Encrypted Vault
        </span>
      </div>

      <div
        className="company-grid"
        style={{
          marginBottom: '24px',
          gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
        }}
      >
        {(
          data?.supportedProviders || [
            {
              name: 'anthropic',
              label: 'Anthropic Claude',
              defaultModel: 'claude-opus-5',
              description: 'Claude Opus 5 (max), Claude Fable 5 (with fallback), Claude Sonnet 5.',
            },
            {
              name: 'openai',
              label: 'OpenAI',
              defaultModel: 'gpt-5.6-sol',
              description: 'GPT-5.6 Sol (max), GPT-5.6 Luna (max), o3-mini (high), o1.',
            },
            {
              name: 'xai',
              label: 'xAI (Grok)',
              defaultModel: 'grok-4.6',
              description: 'Grok 4.6 (high/xhigh), Grok 4.5 — Uncensored contrarian debate.',
            },
            {
              name: 'kimi',
              label: 'Moonshot AI (Kimi)',
              defaultModel: 'kimi-k3',
              description: 'Kimi K3 (max 2.8T parameters, 1M context), Kimi K2.7 Code.',
            },
            {
              name: 'gemini',
              label: 'Google Gemini',
              defaultModel: 'gemini-3.7-flash',
              description: 'Gemini 3.7 Flash (high), Gemini 3.6 Flash, Gemini 3.1 Pro.',
            },
            {
              name: 'deepseek',
              label: 'DeepSeek',
              defaultModel: 'deepseek-v4-pro-0813',
              description: 'DeepSeek V4 Pro 0813 (max), DeepSeek Reasoner (R1), Chat (V3).',
            },
            {
              name: 'zhipu',
              label: 'Zhipu AI (GLM / Z.ai)',
              defaultModel: 'glm-5.2',
              description: 'GLM-5.2 (max), GLM-5V-Turbo — 1M context multimodal reasoning.',
            },
            {
              name: 'nvidia',
              label: 'NVIDIA NIM',
              defaultModel: 'nvidia/nemotron-3-ultra',
              description: 'Nemotron 3 Ultra, Nemotron 3.5 Lightning GPU microservices.',
            },
            {
              name: 'muse',
              label: 'Meta / Muse',
              defaultModel: 'muse-spark-1.2',
              description: 'Muse Spark 1.2 (xhigh), Llama 3.3 70B open-weights intelligence.',
            },
            {
              name: 'groq',
              label: 'Groq (Ultra-Fast LPUs)',
              defaultModel: 'llama-3.3-70b-versatile',
              description: '500+ tok/s instantaneous executive briefings & board debate.',
            },
            {
              name: 'openrouter',
              label: 'OpenRouter Gateway',
              defaultModel: 'anthropic/claude-opus-5',
              description: 'Universal gateway granting instant access to 200+ models.',
            },
            {
              name: 'ollama',
              label: 'Ollama / Local LLM',
              defaultModel: 'deepseek-r1:latest',
              description: '100% private, zero-data-leakage inference on local hardware.',
            },
            {
              name: 'custom',
              label: 'Custom OpenAI-Compatible',
              defaultModel: 'default',
              description: 'Self-hosted vLLM, LM Studio, or private OpenAI endpoint.',
            },
          ]
        ).map((prov: any) => {
          const item = data?.providers?.find((p: any) => p.providerName === prov.name)
          const isSelected = selectedProvider === prov.name
          return (
            <div
              key={prov.name}
              className={`card model-card ${isSelected ? 'selected' : ''}`}
              onClick={() => handleProviderSelect(prov)}
              style={{
                cursor: 'pointer',
                border: isSelected ? '2px solid #0f172a' : '1px solid #e2e8f0',
                background: isSelected ? '#f8fafc' : '#ffffff',
                transition: 'all 0.15s ease',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <strong style={{ fontSize: '1.05rem', color: '#0f172a' }}>{prov.label}</strong>
                {item?.isActive && (
                  <span
                    style={{
                      background: '#dcfce7',
                      color: '#15803d',
                      fontSize: '0.75rem',
                      padding: '2px 8px',
                      borderRadius: '12px',
                      fontWeight: 600,
                    }}
                  >
                    Active
                  </span>
                )}
              </div>
              <p style={{ fontSize: '0.8rem', color: '#64748b', margin: '4px 0 8px', lineHeight: '1.3' }}>
                {prov.description || 'Frontier AI Provider'}
              </p>
              <span style={{ margin: '4px 0', fontSize: '0.82rem', color: '#475569', display: 'block' }}>
                Model: <strong style={{ color: '#0f172a' }}>{item?.selectedModel || prov.defaultModel}</strong>
              </span>
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  fontSize: '0.78rem',
                  color: item?.hasKey || prov.name === 'ollama' ? '#16a34a' : '#94a3b8',
                }}
              >
                {item?.hasKey || prov.name === 'ollama' ? <CheckCircle2 size={13} /> : <CircleDot size={13} />}
                {prov.name === 'ollama'
                  ? 'Local Connection'
                  : item?.hasKey
                  ? `Key saved (${item.maskedApiKey})`
                  : 'No key added'}
              </div>
            </div>
          )
        })}
      </div>

      <section
        className="card editor-modal"
        style={{
          maxWidth: '100%',
          margin: '0',
          background: '#ffffff',
          border: '1px solid #e2e8f0',
        }}
      >
        <div className="modal-header">
          <div>
            <p className="eyebrow">
              <Cpu size={14} /> CONFIGURE {currentProviderInfo?.label?.toUpperCase() || selectedProvider.toUpperCase()}
            </p>
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
            <span>
              Select or Type Model{' '}
              {discoveredModels.length > 0 && (
                <small style={{ color: '#16a34a', fontWeight: 600 }}>
                  ({discoveredModels.length} live models discovered from API)
                </small>
              )}
            </span>
            <div style={{ display: 'flex', gap: '8px' }}>
              <select
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                style={{
                  background: '#ffffff',
                  color: '#0f172a',
                  padding: '10px 12px',
                  borderRadius: '8px',
                  border: '1px solid #e2e8f0',
                  fontSize: '13px',
                  flex: 1.2,
                }}
              >
                {availableModelList.map((m: string) => (
                  <option key={m} value={m}>
                    {m}
                  </option>
                ))}
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
            <span>
              Cognitive Depth & Reasoning Effort{' '}
              <small style={{ color: '#64748b' }}>
                (Controls multi-step deliberation level on C-Suite strategic debates)
              </small>
            </span>
            <div style={{ display: 'flex', gap: '8px' }}>
              {[
                { id: 'max', label: 'Max (Deep Chain-of-Thought)' },
                { id: 'xhigh', label: 'X-High' },
                { id: 'high', label: 'High (Standard Executive)' },
                { id: 'medium', label: 'Medium' },
                { id: 'off', label: 'Instant (No Extended Thinking)' },
              ].map((tier) => (
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
            <span>
              Custom Base URL{' '}
              <small style={{ color: '#64748b' }}>
                (Optional override for self-hosted vLLM, LM Studio, proxies, or Azure)
              </small>
            </span>
            <input
              type="text"
              value={customBaseUrl}
              onChange={(e) => setCustomBaseUrl(e.target.value)}
              placeholder={currentProviderInfo?.defaultBaseUrl || 'e.g. https://api.openai.com/v1'}
              style={{ width: '100%', fontSize: '13px' }}
            />
          </label>

          {selectedProvider !== 'ollama' && (
            <label className="field">
              <span>
                API Key{' '}
                {configuredItem?.hasKey && (
                  <small style={{ color: '#71717a' }}>(Saved: {configuredItem.maskedApiKey})</small>
                )}
              </span>
              <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
                <input
                  type={showKey ? 'text' : 'password'}
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder={
                    configuredItem?.hasKey
                      ? 'Leave blank to keep existing key, or paste new key'
                      : 'Paste API key here...'
                  }
                  style={{ width: '100%', paddingRight: '40px' }}
                />
                <button
                  type="button"
                  onClick={() => setShowKey(!showKey)}
                  style={{
                    position: 'absolute',
                    right: '10px',
                    background: 'none',
                    border: 'none',
                    color: '#a1a1aa',
                    cursor: 'pointer',
                  }}
                >
                  {showKey ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </label>
          )}
        </div>

        {testStatus && (
          <div
            style={{
              marginBottom: '16px',
              padding: '10px 14px',
              borderRadius: '8px',
              background: testStatus.includes('✓') ? 'rgba(34,197,94,0.1)' : 'rgba(239,68,68,0.1)',
              border: testStatus.includes('✓') ? '1px solid rgba(34,197,94,0.3)' : '1px solid rgba(239,68,68,0.3)',
              color: testStatus.includes('✓') ? '#16a34a' : '#dc2626',
              fontSize: '0.9rem',
            }}
          >
            <strong>Status:</strong> {testStatus}
          </div>
        )}

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

      <section
        className="card editor-modal"
        style={{
          maxWidth: '100%',
          marginTop: '24px',
          background: '#ffffff',
          border: '1px solid #e2e8f0',
        }}
      >
        <div className="modal-header">
          <div>
            <p className="eyebrow">
              <ShieldCheck size={14} style={{ color: '#2563eb' }} /> SECURITY POSTURE & ACTION POLICY (YC QM STANDARD)
            </p>
            <h2>Execution Safety Gates</h2>
            <p className="subhead">
              Govern how autonomous agent tasks and draft actions are staged and executed.
            </p>
          </div>
        </div>
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: '12px',
            margin: '16px 0',
          }}
        >
          <div
            style={{
              padding: '12px 14px',
              borderRadius: '8px',
              border: '2px solid #2563eb',
              background: '#eff6ff',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
              <strong style={{ fontSize: '0.85rem', color: '#1e40af' }}>Auto (Default)</strong>
              <span
                style={{
                  fontSize: '10px',
                  background: '#dbeafe',
                  color: '#1d4ed8',
                  padding: '1px 6px',
                  borderRadius: '4px',
                  fontWeight: 700,
                }}
              >
                ACTIVE
              </span>
            </div>
            <p style={{ margin: 0, fontSize: '11px', color: '#3b82f6', lineHeight: '1.4' }}>
              Inbound text is screened for prompt injection. Safe action drafts are auto-staged for review.
            </p>
          </div>
          <div
            style={{
              padding: '12px 14px',
              borderRadius: '8px',
              border: '1px solid #cbd5e1',
              background: '#f8fafc',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
              <strong style={{ fontSize: '0.85rem', color: '#334155' }}>Strict</strong>
            </div>
            <p style={{ margin: 0, fontSize: '11px', color: '#64748b', lineHeight: '1.4' }}>
              Every autonomous task and tool call pauses for explicit human-in-the-loop sign-off.
            </p>
          </div>
          <div
            style={{
              padding: '12px 14px',
              borderRadius: '8px',
              border: '1px solid #cbd5e1',
              background: '#f8fafc',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
              <strong style={{ fontSize: '0.85rem', color: '#334155' }}>Dangerous</strong>
            </div>
            <p style={{ margin: 0, fontSize: '11px', color: '#64748b', lineHeight: '1.4' }}>
              Autonomous tool execution without human confirmation (for sandbox testing).
            </p>
          </div>
        </div>
        <div
          style={{
            background: '#f8fafc',
            padding: '10px 14px',
            borderRadius: '6px',
            fontSize: '11px',
            color: '#475569',
            border: '1px solid #e2e8f0',
          }}
        >
          <strong>Command & Action Policy Filter:</strong> Active rules intercept destructive SQL (DROP TABLE), recursive deletes (rm -rf), force pushes, and secret exposure.
        </div>
      </section>

      {/* Real-time AI Token Burn & Observability Section */}
      <section
        className="card editor-modal"
        style={{
          maxWidth: '100%',
          marginTop: '32px',
          background: '#ffffff',
          border: '1px solid #e2e8f0',
        }}
      >
        <div className="modal-header">
          <div>
            <p className="eyebrow" style={{ color: '#0284c7', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Activity size={14} /> LIVE AI TELEMETRY & COST LEDGER
            </p>
            <h2>AI Token Burn & Model ROI</h2>
            <p className="subhead">
              Real-time inference tracking, token consumption, and dynamic cost accounting across multi-agent board workflows.
            </p>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '24px' }}>
          <div style={{ background: '#f8fafc', padding: '16px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
            <div style={{ fontSize: '12px', color: '#64748b', display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
              <DollarSign size={14} color="#059669" /> Total AI Spend
            </div>
            <div style={{ fontSize: '24px', fontWeight: '700', color: '#0f172a' }}>
              ${observabilityData ? observabilityData.totalCostUsd.toFixed(4) : '0.0000'}
            </div>
          </div>

          <div style={{ background: '#f8fafc', padding: '16px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
            <div style={{ fontSize: '12px', color: '#64748b', display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
              <Layers size={14} color="#2563eb" /> Total Tokens
            </div>
            <div style={{ fontSize: '24px', fontWeight: '700', color: '#0f172a' }}>
              {observabilityData ? observabilityData.totalTokens.toLocaleString() : '0'}
            </div>
          </div>

          <div style={{ background: '#f8fafc', padding: '16px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
            <div style={{ fontSize: '12px', color: '#64748b', display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
              <Cpu size={14} color="#7c3aed" /> Total Inferences
            </div>
            <div style={{ fontSize: '24px', fontWeight: '700', color: '#0f172a' }}>
              {observabilityData ? observabilityData.totalInferences : '0'}
            </div>
          </div>

          <div style={{ background: '#f8fafc', padding: '16px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
            <div style={{ fontSize: '12px', color: '#64748b', display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
              <Timer size={14} color="#ea580c" /> Avg Latency
            </div>
            <div style={{ fontSize: '24px', fontWeight: '700', color: '#0f172a' }}>
              {observabilityData ? `${observabilityData.avgLatencyMs.toFixed(0)} ms` : '0 ms'}
            </div>
          </div>
        </div>

        {observabilityData && Object.keys(observabilityData.providerBreakdown).length > 0 && (
          <div style={{ borderTop: '1px solid #e2e8f0', paddingTop: '16px' }}>
            <h4 style={{ fontSize: '13px', fontWeight: '600', color: '#334155', marginBottom: '12px' }}>
              Provider Cost Breakdown
            </h4>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '12px' }}>
              {Object.entries(observabilityData.providerBreakdown).map(([prov, stats]) => (
                <div
                  key={prov}
                  style={{
                    padding: '12px',
                    borderRadius: '6px',
                    border: '1px solid #e2e8f0',
                    background: '#ffffff',
                    fontSize: '12px',
                  }}
                >
                  <div style={{ fontWeight: '600', textTransform: 'capitalize', color: '#0f172a', marginBottom: '4px' }}>
                    {prov}
                  </div>
                  <div style={{ color: '#64748b', display: 'flex', justifyContent: 'space-between' }}>
                    <span>Inferences: {stats.calls}</span>
                    <span>Tokens: {stats.totalTokens.toLocaleString()}</span>
                  </div>
                  <div style={{ color: '#059669', fontWeight: '600', marginTop: '4px' }}>
                    Est. Cost: ${stats.costUsd.toFixed(4)}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </section>

      <section
        className="card editor-modal danger-zone"
        style={{
          maxWidth: '100%',
          marginTop: '32px',
          background: '#ffffff',
          border: '1px solid #fecaca',
        }}
      >
        <div className="modal-header">
          <div>
            <p className="eyebrow" style={{ color: '#ef4444' }}>
              <Flame size={14} /> DANGER ZONE
            </p>
            <h2>Reset Workspace</h2>
            <p className="subhead">
              This will permanently delete all company data, founder context, agent action history, and vector embeddings from the FounderOS database.
            </p>
          </div>
        </div>
        <div className="modal-footer" style={{ justifyContent: 'flex-start' }}>
          <button
            className="primary-button"
            style={{ background: '#ef4444', color: 'white', border: 'none' }}
            onClick={onReset}
          >
            Delete Profile & Start Fresh
          </button>
        </div>
      </section>
    </div>
  )
}

