import { useState } from 'react'
import { ChevronRight, X, Check } from 'lucide-react'
import { type CompanyProfile, type FounderProfile } from '../domain'

export function Field({
  label,
  value,
  onChange,
}: {
  label: string
  value: string
  onChange: (value: string) => void
}) {
  return (
    <label className="field">
      <span>{label}</span>
      <input value={value} onChange={(event) => onChange(event.target.value)} />
    </label>
  )
}

export function NumberField({
  label,
  value,
  onChange,
}: {
  label: string
  value: number
  onChange: (value: number) => void
}) {
  return (
    <label className="field">
      <span>{label}</span>
      <input
        type="number"
        min="0"
        value={value}
        onChange={(event) => onChange(parseInt(event.target.value) || 0)}
      />
    </label>
  )
}

export function SelectField({
  label,
  value,
  options,
  onChange,
}: {
  label: string
  value: string
  options: string[]
  onChange: (value: string) => void
}) {
  return (
    <label className="field">
      <span>{label}</span>
      <select value={value} onChange={(event) => onChange(event.target.value)}>
        {options.map((opt) => (
          <option key={opt} value={opt}>
            {opt}
          </option>
        ))}
      </select>
    </label>
  )
}

export function CompanyEditor({
  company,
  onSave,
  onClose,
}: {
  company: CompanyProfile
  onSave: (company: CompanyProfile) => void
  onClose: () => void
}) {
  const [draft, setDraft] = useState(company)
  const update = (field: keyof CompanyProfile, value: any) =>
    setDraft((current) => ({ ...current, [field]: value }))

  const businessModels = [
    'B2B SaaS',
    'B2C / D2C',
    'Marketplace',
    'Agency / Services',
    'Hardware / Manufacturing',
    'Open Source',
    'Other',
  ]
  const platformFocuses = [
    'Web Application',
    'Mobile App',
    'API / Developer Tools',
    'Chrome Extension',
    'Offline / Retail',
    'Other',
  ]
  const fundingStates = [
    'Bootstrapped',
    'Pre-Seed',
    'Seed',
    'Series A',
    'Series B+',
    'Public',
  ]
  const revenueRanges = ['Pre-revenue', '<$10k MRR', '$10k-$100k MRR', '$1M+ ARR']
  const stages = ['Idea stage', 'Pre-revenue', 'Early revenue', 'Growth stage', 'Scale']
  const teamSizes = [
    'Solo founder',
    '2-5 people',
    '6-15 people',
    '16-50 people',
    '50+ people',
  ]

  return (
    <div
      className="modal-backdrop"
      role="presentation"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <section
        className="editor-modal"
        role="dialog"
        aria-modal="true"
        aria-label="Edit company model"
      >
        <div className="modal-header">
          <div>
            <p className="eyebrow">COMPANY MODEL</p>
            <h2>Refine FounderOS’s context</h2>
          </div>
          <button className="icon-button" onClick={onClose} aria-label="Close editor">
            <X size={18} />
          </button>
        </div>
        <p className="modal-copy">
          These fields influence how the system ranks trade-offs and recommendations.
        </p>
        <div
          className="form-grid single editor-fields"
          style={{ maxHeight: '60vh', overflowY: 'auto', paddingRight: '10px' }}
        >
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
          <button className="secondary-button" onClick={onClose}>
            Cancel
          </button>
          <button className="primary-button" onClick={() => onSave(draft)}>
            Save company model <Check size={15} />
          </button>
        </div>
      </section>
    </div>
  )
}

export function FounderEditor({
  founder,
  onSave,
  onClose,
}: {
  founder: FounderProfile
  onSave: (founder: FounderProfile) => void
  onClose: () => void
}) {
  const [draft, setDraft] = useState(founder)
  const update = (field: keyof FounderProfile, value: any) =>
    setDraft((current) => ({ ...current, [field]: value }))

  const founderRoles = ['Solo Founder', 'CEO', 'CTO', 'COO', 'Other']
  const founderBackgrounds = [
    'Engineering / Technical',
    'Product / Design',
    'Sales / Go-to-Market',
    'Operations / Finance',
    'Marketing / Growth',
  ]
  const experienceLevels = [
    'First-time Founder',
    'Second-time Founder',
    'Serial Founder (3+)',
    'Industry Veteran (10+ yrs)',
  ]
  const founderSuperpowers = [
    'Building & Engineering',
    'Sales & Closing Deals',
    'Product Vision & UX',
    'Fundraising & Capital',
    'Recruiting & Team Building',
  ]

  return (
    <div
      className="modal-backdrop"
      role="presentation"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <section
        className="editor-modal"
        role="dialog"
        aria-modal="true"
        aria-label="Edit founder profile"
      >
        <div className="modal-header">
          <div>
            <p className="eyebrow">FOUNDER PROFILE</p>
            <h2>Who is driving the ship?</h2>
          </div>
          <button className="icon-button" onClick={onClose} aria-label="Close editor">
            <X size={18} />
          </button>
        </div>
        <p className="modal-copy">
          Update your strengths and gaps to receive better executive advice.
        </p>
        <div
          className="form-grid single editor-fields"
          style={{ maxHeight: '60vh', overflowY: 'auto', paddingRight: '10px' }}
        >
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
          <button className="secondary-button" onClick={onClose}>
            Cancel
          </button>
          <button className="primary-button" onClick={() => onSave(draft)}>
            Save founder profile <Check size={15} />
          </button>
        </div>
      </section>
    </div>
  )
}

export function CompanyView({
  company,
  connectedCount,
  onEdit,
  onConnections,
}: {
  company: CompanyProfile
  connectedCount: number
  onEdit: () => void
  onConnections: () => void
}) {
  return (
    <div className="page simple-page">
      <div className="simple-heading">
        <div>
          <p className="eyebrow">COMPANY MODEL</p>
          <h1>{company.name}</h1>
          <p className="subhead">The shared operating context that grounds every recommendation.</p>
        </div>
        <button className="secondary-button" onClick={onEdit}>
          Edit company model
        </button>
      </div>
      <div className="company-grid">
        <article className="card model-card">
          <span>Business model</span>
          <strong>{company.businessModel}</strong>
          <span>Funding</span>
          <strong>{company.fundingState}</strong>
          <span>Platform</span>
          <strong>{company.platformFocus}</strong>
          <span>Stage</span>
          <strong>{company.stage}</strong>
        </article>
        <article className="card model-card">
          <span>Current objective</span>
          <strong>{company.objective}</strong>
          <span>Primary constraint</span>
          <strong>{company.primaryConstraint}</strong>
          <span>Primary Metric</span>
          <strong>{company.primaryMetric}</strong>
          <span>Runway floor</span>
          <strong>{company.runwayMonths} months</strong>
        </article>
        <article className="card model-card">
          <span>Connected sources</span>
          <strong>
            {connectedCount
              ? `${connectedCount} source${connectedCount > 1 ? 's' : ''} configured`
              : 'No sources configured'}
          </strong>
          <p className="model-caption">
            Sources add evidence; they never receive execution access by default.
          </p>
          <button className="text-button" onClick={onConnections}>
            Manage sources <ChevronRight size={16} />
          </button>
        </article>
      </div>
    </div>
  )
}

