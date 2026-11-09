import { X } from 'lucide-react'

export function NotificationsDropdown({ onClose }: { onClose: () => void }) {
  return (
    <div
      className="toast"
      style={{
        top: '68px',
        right: '40px',
        width: '320px',
        flexDirection: 'column',
        alignItems: 'flex-start',
      }}
    >
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          width: '100%',
          borderBottom: '1px solid #334155',
          paddingBottom: '8px',
          marginBottom: '8px',
        }}
      >
        <strong>System Notifications</strong>
        <button
          onClick={onClose}
          style={{ background: 'none', border: 0, color: '#94a3b8', cursor: 'pointer' }}
        >
          <X size={14} />
        </button>
      </div>
      <div style={{ fontSize: '12px', color: '#cbd5e1', lineHeight: '1.5' }}>
        <div>✓ Worker: Background signal ingestion complete (3 items).</div>
        <div style={{ marginTop: '6px' }}>✓ Scheduler: Decision ledger review dates verified.</div>
        <div style={{ marginTop: '6px' }}>✓ Vault: AES-256-GCM token encryption active.</div>
      </div>
    </div>
  )
}

