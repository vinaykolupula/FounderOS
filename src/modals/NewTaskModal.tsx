import { useState, useEffect } from 'react'
import { ListTodo, X, Check } from 'lucide-react'

export function NewTaskModal({
  onClose,
  onSave,
}: {
  onClose: () => void
  onSave: (task: any) => void
}) {
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

  return (
    <div
      className="modal-backdrop"
      role="presentation"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <section className="editor-modal" role="dialog" aria-modal="true" style={{ maxWidth: '560px' }}>
        <div className="modal-header">
          <div>
            <p className="eyebrow" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <ListTodo size={14} /> FOUNDER WORKFLOW
            </p>
            <h2>Record New Founder Task</h2>
          </div>
          <button className="icon-button" onClick={onClose} aria-label="Close modal">
            <X size={18} />
          </button>
        </div>
        <p className="modal-copy">Add an urgent founder task or delegate it directly to FounderOS.</p>

        <div className="form-grid single editor-fields" style={{ margin: '16px 0' }}>
          <label className="field">
            <span>Task Title</span>
            <input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Review legal terms for enterprise contract"
            />
          </label>
          <label className="field">
            <span>Description / Details</span>
            <input
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="e.g. Atlas Logistics requires uptime SLA confirmation"
            />
          </label>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '10px' }}>
            <label className="field">
              <span>Priority</span>
              <select
                value={priority}
                onChange={(e) => setPriority(e.target.value)}
                style={{
                  width: '100%',
                  height: '40px',
                  borderRadius: '8px',
                  border: '1px solid #e2e8f0',
                  padding: '0 10px',
                  fontSize: '13px',
                }}
              >
                <option value="P0_CRITICAL">P0 Critical</option>
                <option value="P1_HIGH">P1 High</option>
                <option value="P2_MEDIUM">P2 Medium</option>
                <option value="P3_LOW">P3 Low</option>
              </select>
            </label>
            <label className="field">
              <span>Category</span>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                style={{
                  width: '100%',
                  height: '40px',
                  borderRadius: '8px',
                  border: '1px solid #e2e8f0',
                  padding: '0 10px',
                  fontSize: '13px',
                }}
              >
                <option value="TODAY">Today</option>
                <option value="UPCOMING">Upcoming</option>
                <option value="DELEGATED">Delegated</option>
              </select>
            </label>
            <label className="field">
              <span>Due Date</span>
              <input
                value={dueDate}
                onChange={(e) => setDueDate(e.target.value)}
                placeholder="e.g. Today 5:00 PM"
              />
            </label>
          </div>
        </div>

        <div className="modal-footer">
          <button className="secondary-button" onClick={onClose}>
            Cancel
          </button>
          <button
            className="primary-button"
            onClick={() => title && onSave({ title, description, priority, category, dueDate })}
          >
            Save Task <Check size={15} />
          </button>
        </div>
      </section>
    </div>
  )
}

