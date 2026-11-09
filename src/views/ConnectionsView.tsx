import { ShieldCheck, Database, Mail, CircleDot, Plug, CheckCircle2, ChevronRight } from 'lucide-react'
import { type Connector, type ConnectorId } from '../domain'

export function ConnectionsView({
  connectors,
  onConfigure,
}: {
  connectors: Connector[]
  onConfigure: (id: ConnectorId) => void
}) {
  return (
    <div className="page simple-page">
      <div className="simple-heading">
        <div>
          <p className="eyebrow">INTEGRATION LAYER</p>
          <h1>Connections</h1>
          <p className="subhead">Choose the trusted company systems that can inform your operating brief.</p>
        </div>
        <span className="approval-note">
          <ShieldCheck size={15} /> Read access first
        </span>
      </div>
      <section className="connection-note">
        <Database size={18} />
        <div>
          <strong>Connection setup is local and intentional.</strong>
          <p>
            This prototype records your chosen sources only. Real data access will require per-service OAuth, scoped credentials, and an audit trail.
          </p>
        </div>
      </section>
      <section className="connection-grid">
        {connectors.map((connector) => (
          <article className="connection-card" key={connector.id}>
            <div className="connection-icon">
              {connector.id === 'gmail' ? (
                <Mail size={19} />
              ) : connector.id === 'linear' ? (
                <CircleDot size={19} />
              ) : (
                <Plug size={19} />
              )}
            </div>
            <div className="connection-copy">
              <span>{connector.category}</span>
              <h3>{connector.name}</h3>
              <p>{connector.description}</p>
            </div>
            <div className="connection-footer">
              <div className={`connection-status ${connector.status}`}>
                {connector.status === 'configured' ? (
                  <CheckCircle2 size={14} />
                ) : (
                  <CircleDot size={14} />
                )}
                {connector.status === 'configured' ? 'Setup saved' : 'Not connected'}
              </div>
              <button
                className={connector.status === 'configured' ? 'secondary-button' : 'primary-button'}
                onClick={() => onConfigure(connector.id)}
              >
                {connector.status === 'configured' ? 'Review setup' : 'Set up'} <ChevronRight size={14} />
              </button>
            </div>
          </article>
        ))}
      </section>
    </div>
  )
}

