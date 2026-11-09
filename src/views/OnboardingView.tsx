import { useState } from 'react'
import { ChevronRight, ArrowUpRight, Sparkles, Check, Plus } from 'lucide-react'
import {
  type CompanyProfile,
  type FounderProfile,
  type ConnectorId,
  defaultCompany,
  defaultFounder,
} from '../domain'
import { Field, SelectField, NumberField } from './CompanyView'

export function OnboardingView({
  onComplete,
}: {
  onComplete: (
    company: CompanyProfile,
    founder: FounderProfile,
    selected: ConnectorId[]
  ) => void
}) {
  const [step, setStep] = useState(1)
  const [company, setCompany] = useState(defaultCompany)
  const [founder, setFounder] = useState(defaultFounder)
  const [selected, setSelected] = useState<ConnectorId[]>([])
  const updateCompany = (field: keyof CompanyProfile, value: any) =>
    setCompany((current) => ({ ...current, [field]: value }))
  const updateFounder = (field: keyof FounderProfile, value: any) =>
    setFounder((current) => ({ ...current, [field]: value }))
  const toggle = (id: ConnectorId) =>
    setSelected((current) =>
      current.includes(id) ? current.filter((item) => item !== id) : [...current, id]
    )

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
    <main className="onboarding-shell">
      <section className="onboarding-panel">
        <div className="onboarding-brand">
          <img src="/media/Logo.webp" alt="FounderOS Logo" className="brand-logo-img" />
          FounderOS
        </div>
        <div className="stepper">
          <span className={step >= 1 ? 'current' : ''}>01</span>
          <i />
          <span className={step >= 2 ? 'current' : ''}>02</span>
          <i />
          <span className={step >= 3 ? 'current' : ''}>03</span>
          <i />
          <span className={step >= 4 ? 'current' : ''}>04</span>
          <i />
          <span className={step >= 5 ? 'current' : ''}>05</span>
        </div>
        {step === 1 && (
          <>
            <p className="eyebrow">IDENTITY & DIGITAL FOOTPRINT</p>
            <h1>Start with the company FounderOS should understand.</h1>
            <p className="onboarding-copy">
              This context gives the agent a foundation to search and scrape intelligently.
            </p>
            <div className="form-grid">
              <Field
                label="Company name"
                value={company.name}
                onChange={(value) => updateCompany('name', value)}
              />
              <Field
                label="Website URL (e.g. https://...)"
                value={company.websiteUrl || ''}
                onChange={(value) => updateCompany('websiteUrl', value)}
              />
              <Field
                label="LinkedIn Profile"
                value={company.linkedinUrl || ''}
                onChange={(value) => updateCompany('linkedinUrl', value)}
              />
              <Field
                label="Social / Twitter"
                value={company.socialUrl || ''}
                onChange={(value) => updateCompany('socialUrl', value)}
              />
            </div>
          </>
        )}
        {step === 2 && (
          <>
            <p className="eyebrow">FOUNDER DNA</p>
            <h1>Who is building {company.name || 'this'}?</h1>
            <p className="onboarding-copy">
              Your strengths and gaps define where the AI should actively lean in vs stay back.
            </p>
            <div className="form-grid">
              <Field
                label="Your name"
                value={founder.name}
                onChange={(value) => updateFounder('name', value)}
              />
              <SelectField
                label="Role"
                value={founder.role}
                options={founderRoles}
                onChange={(value) => updateFounder('role', value)}
              />
              <SelectField
                label="Core Background"
                value={founder.background}
                options={founderBackgrounds}
                onChange={(value) => updateFounder('background', value)}
              />
              <SelectField
                label="Experience Level"
                value={founder.experienceLevel}
                options={experienceLevels}
                onChange={(value) => updateFounder('experienceLevel', value)}
              />
              <Field
                label="Domain Expertise"
                value={founder.domainExpertise}
                onChange={(value) => updateFounder('domainExpertise', value)}
              />
              <SelectField
                label="Your Superpower (Strongest skill)"
                value={founder.superpower}
                options={founderSuperpowers}
                onChange={(value) => updateFounder('superpower', value)}
              />
              <SelectField
                label="Your Primary Gap (Weakest skill)"
                value={founder.primaryGap}
                options={founderSuperpowers}
                onChange={(value) => updateFounder('primaryGap', value)}
              />
              <Field
                label="Current Learning Focus"
                value={founder.learningFocus}
                onChange={(value) => updateFounder('learningFocus', value)}
              />
              <Field
                label="Communication Style (e.g. Direct, Brief)"
                value={founder.communicationStyle || ''}
                onChange={(value) => updateFounder('communicationStyle', value)}
              />
              <Field
                label="Energy State (e.g. Sprinting, Burned out)"
                value={founder.energyState || ''}
                onChange={(value) => updateFounder('energyState', value)}
              />
              <Field
                label="Core Values (e.g. Speed, Quality)"
                value={founder.coreValues || ''}
                onChange={(value) => updateFounder('coreValues', value)}
              />
            </div>
          </>
        )}
        {step === 3 && (
          <>
            <p className="eyebrow">ARCHITECTURE & SCALE</p>
            <h1>How does {company.name || 'the company'} operate?</h1>
            <p className="onboarding-copy">
              This architecture helps the agent calibrate its growth and execution advice.
            </p>
            <div className="form-grid">
              <SelectField
                label="Business Model"
                value={company.businessModel || ''}
                options={businessModels}
                onChange={(value) => updateCompany('businessModel', value)}
              />
              <SelectField
                label="Platform Focus"
                value={company.platformFocus || ''}
                options={platformFocuses}
                onChange={(value) => updateCompany('platformFocus', value)}
              />
              <SelectField
                label="Funding State"
                value={company.fundingState || ''}
                options={fundingStates}
                onChange={(value) => updateCompany('fundingState', value)}
              />
              <SelectField
                label="Revenue Range"
                value={company.revenueRange || ''}
                options={revenueRanges}
                onChange={(value) => updateCompany('revenueRange', value)}
              />
              <SelectField
                label="Company stage"
                value={company.stage}
                options={stages}
                onChange={(value) => updateCompany('stage', value)}
              />
              <SelectField
                label="Team size"
                value={company.teamSize}
                options={teamSizes}
                onChange={(value) => updateCompany('teamSize', value)}
              />
              <Field
                label="GTM Motion (e.g. PLG, Sales-led)"
                value={company.gtmMotion || ''}
                onChange={(value) => updateCompany('gtmMotion', value)}
              />
              <Field
                label="Burn Rate (e.g. $50k/mo)"
                value={company.burnRate || ''}
                onChange={(value) => updateCompany('burnRate', value)}
              />
            </div>
          </>
        )}
        {step === 4 && (
          <>
            <p className="eyebrow">STRATEGIC COMPASS</p>
            <h1>What are you trying to make true?</h1>
            <p className="onboarding-copy">
              FounderOS uses these objectives and constraints to rank what matters.
            </p>
            <div className="form-grid single">
              <Field
                label="Current objective"
                value={company.objective}
                onChange={(value) => updateCompany('objective', value)}
              />
              <Field
                label="Ideal customer"
                value={company.idealCustomer}
                onChange={(value) => updateCompany('idealCustomer', value)}
              />
              <Field
                label="Primary Metric"
                value={company.primaryMetric}
                onChange={(value) => updateCompany('primaryMetric', value)}
              />
              <Field
                label="Primary constraint right now"
                value={company.primaryConstraint}
                onChange={(value) => updateCompany('primaryConstraint', value)}
              />
              <NumberField
                label="Minimum runway (months)"
                value={company.runwayMonths}
                onChange={(value) => updateCompany('runwayMonths', value)}
              />
              <Field
                label="Tech Stack"
                value={company.techStack || ''}
                onChange={(value) => updateCompany('techStack', value)}
              />
              <Field
                label="Competitive Moat"
                value={company.competitiveMoat || ''}
                onChange={(value) => updateCompany('competitiveMoat', value)}
              />
            </div>
          </>
        )}
        {step === 5 && (
          <>
            <p className="eyebrow">SIGNAL SOURCES</p>
            <h1>Choose the first systems to connect.</h1>
            <p className="onboarding-copy">
              We will create secure connection setup for your selected sources. No information leaves your workspace until you complete OAuth.
            </p>
            <div className="source-picker">
              {(['gmail', 'slack', 'linear', 'hubspot', 'stripe'] as ConnectorId[]).map((id) => (
                <button
                  className={`source-option ${selected.includes(id) ? 'selected' : ''}`}
                  onClick={() => toggle(id)}
                  key={id}
                >
                  <span className="pick-icon">
                    {selected.includes(id) ? <Check size={15} /> : <Plus size={15} />}
                  </span>
                  <span>
                    <strong>{id === 'gmail' ? 'Google Workspace' : id[0].toUpperCase() + id.slice(1)}</strong>
                    <small>
                      {id === 'gmail'
                        ? 'Email and calendar'
                        : id === 'linear'
                        ? 'Product execution'
                        : id === 'hubspot'
                        ? 'Pipeline and customer data'
                        : id === 'stripe'
                        ? 'Revenue and subscriptions'
                        : 'Team context and decisions'}
                    </small>
                  </span>
                </button>
              ))}
            </div>
          </>
        )}
        <div className="onboarding-footer">
          <button
            className="back-step"
            onClick={() => setStep((current) => Math.max(1, current - 1))}
            disabled={step === 1}
          >
            Back
          </button>
          {step < 5 ? (
            <button className="primary-button wide" onClick={() => setStep((current) => current + 1)}>
              Continue <ChevronRight size={16} />
            </button>
          ) : (
            <button
              className="primary-button wide"
              onClick={() => onComplete(company, founder, selected)}
            >
              Open command center <ArrowUpRight size={16} />
            </button>
          )}
        </div>
      </section>
      <aside className="onboarding-aside">
        <div className="aside-pill">
          <Sparkles size={14} /> BUILT FOR FOUNDER JUDGMENT
        </div>
        <blockquote>“An always-on founder intelligence system.”</blockquote>
        <div className="aside-rule" />
        <p>
          It deeply understands your company constraints, monitors real-time signals, and automates high-leverage execution—always keeping you in the driver's seat.
        </p>
      </aside>
    </main>
  )
}

