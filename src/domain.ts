/**
 * FounderOS TypeScript Domain Definitions & Default Factories
 * 
 * Defines all frontend data contracts, workspace entities, founder DNA schemas,
 * company architecture types, and default fallback states.
 */

export type View = 'Overview' | 'Tasks' | 'Executive' | 'Decisions' | 'Intelligence' | 'Company' | 'Connections' | 'Models'

/**
 * Task item entity monitored or executed by the AI agent
 */
export type TaskItem = {
  id: number
  title: string
  description?: string
  priority: 'P0_CRITICAL' | 'P1_HIGH' | 'P2_MEDIUM' | 'P3_LOW'
  category: 'TODAY' | 'UPCOMING' | 'DELEGATED'
  source: 'EMAIL' | 'CALENDAR' | 'LINEAR' | 'FOUNDER_MANUAL' | 'AGENT_MONITOR'
  status: 'PENDING' | 'IN_PROGRESS' | 'DELEGATED' | 'COMPLETED' | 'FAILED'
  due_date?: string
  agent_note?: string
}

export type BusinessModel = 'B2B SaaS' | 'B2C / D2C' | 'Marketplace' | 'Agency / Services' | 'Hardware / Manufacturing' | 'Open Source' | 'Other'
export type PlatformFocus = 'Web Application' | 'Mobile App' | 'API / Developer Tools' | 'Chrome Extension' | 'Offline / Retail' | 'Other'
export type FundingState = 'Bootstrapped' | 'Pre-Seed' | 'Seed' | 'Series A' | 'Series B+' | 'Public'
export type RevenueRange = 'Pre-revenue' | '<$10k MRR' | '$10k-$100k MRR' | '$1M+ ARR'
export type Stage = 'Idea stage' | 'Pre-revenue' | 'Early revenue' | 'Growth stage' | 'Scale'
export type TeamSize = 'Solo founder' | '2-5 people' | '6-15 people' | '16-50 people' | '50+ people'

export type FounderRole = 'Solo Founder' | 'CEO' | 'CTO' | 'COO' | 'Other'
export type FounderBackground = 'Engineering / Technical' | 'Product / Design' | 'Sales / Go-to-Market' | 'Operations / Finance' | 'Marketing / Growth'
export type ExperienceLevel = 'First-time Founder' | 'Second-time Founder' | 'Serial Founder (3+)' | 'Industry Veteran (10+ yrs)'
export type FounderSuperpower = 'Building & Engineering' | 'Sales & Closing Deals' | 'Product Vision & UX' | 'Fundraising & Capital' | 'Recruiting & Team Building'

/**
 * Founder Personal DNA & Psychological Harness Context
 */
export type FounderProfile = {
  name: string
  role: string
  background: string
  experienceLevel: string
  domainExpertise: string
  superpower: string
  primaryGap: string
  learningFocus: string
  // Deep Founder Context
  communicationStyle?: string
  energyState?: string
  coreValues?: string
}

/**
 * Company Architecture Harness Context
 */
export interface CompanyProfile {
  name: string
  websiteUrl?: string
  linkedinUrl?: string
  socialUrl?: string
  businessModel?: string
  platformFocus?: string
  fundingState?: string
  revenueRange?: string
  stage: string
  teamSize: string
  idealCustomer: string
  objective: string
  primaryMetric: string
  primaryConstraint: string
  runwayMonths: number
  // Deep Company Context
  burnRate?: string
  gtmMotion?: string
  techStack?: string
  competitiveMoat?: string
}

export type ConnectorId = 'gmail' | 'slack' | 'linear' | 'hubspot' | 'stripe'

export type Connector = {
  id: ConnectorId
  name: string
  description: string
  category: string
  status: 'not_connected' | 'configured'
}

/**
 * Approval-gated Action Item draft
 */
export type ActionItem = {
  id: number
  title: string
  detail: string
  source: string
  status: 'Ready' | 'Draft'
}

export interface MorningBriefing {
  date: string
  executiveSummary: string
  overnightChanges: string[]
  omtmStatus: string
  topPriorityFocus: string
  energyAdvice: string
}

/**
 * Root Workspace Domain Entity
 */
export type Workspace = {
  id?: string
  isOnboarded: boolean
  company: CompanyProfile
  founder: FounderProfile
  actions: ActionItem[]
  connectors: Connector[]
  decisions?: any[]
  tasks?: TaskItem[]
}

/** Default Founder Profile initialization state */
export const defaultFounder: FounderProfile = {
  name: '',
  role: 'CEO',
  background: 'Engineering / Technical',
  experienceLevel: 'First-time Founder',
  domainExpertise: 'SaaS / B2B',
  superpower: 'Building & Engineering',
  primaryGap: 'Sales & Closing Deals',
  learningFocus: 'GTM & Enterprise Sales',
  communicationStyle: 'Direct and brief',
  energyState: 'Steady pace',
  coreValues: 'Speed, Customer Obsession'
}

/** Default Company Profile initialization state */
export const defaultCompany: CompanyProfile = {
  name: 'FounderOS',
  websiteUrl: '',
  linkedinUrl: '',
  socialUrl: '',
  businessModel: 'B2B SaaS',
  platformFocus: 'Web Application',
  fundingState: 'Bootstrapped',
  revenueRange: '$10k-$100k MRR',
  stage: 'Early revenue',
  teamSize: '2-5 people',
  idealCustomer: 'Mid-market logistics teams',
  objective: 'Reach $60k MRR with sustainable activation',
  primaryMetric: 'Weekly activated accounts',
  primaryConstraint: 'First-value completion',
  runwayMonths: 12,
  burnRate: 'Unknown',
  gtmMotion: 'Product-Led Growth',
  techStack: 'React, Node.js, Postgres',
  competitiveMoat: 'First mover advantage'
}

/**
 * Factory function creating a clean Workspace default instance
 */
export function createWorkspace(): Workspace {
  return {
    isOnboarded: false,
    company: defaultCompany,
    founder: defaultFounder,
    connectors: [
      { id: 'gmail', name: 'Google Workspace', description: 'Email and calendar signals', category: 'Communication', status: 'not_connected' },
      { id: 'slack', name: 'Slack', description: 'Team decisions and delivery context', category: 'Communication', status: 'not_connected' },
      { id: 'linear', name: 'Linear', description: 'Product and engineering execution', category: 'Product', status: 'not_connected' },
      { id: 'hubspot', name: 'HubSpot', description: 'Deals, pipeline, and customer history', category: 'Revenue', status: 'not_connected' },
      { id: 'stripe', name: 'Stripe', description: 'Revenue, subscriptions, and churn', category: 'Finance', status: 'not_connected' },
    ],
    actions: [],
    decisions: [
      { id: 1, decisionCode: '#024', title: 'Pause Feature B. Fix activation first.', detail: 'Correlates with a 12% fall in First-value completion.', status: 'Open' },
      { id: 2, decisionCode: '#023', title: 'Delay Enterprise Tier launch by 2 weeks', detail: 'Single Sign-On SSO telemetry bugs require resolution.', status: 'Validated' },
      { id: 3, decisionCode: '#022', title: 'Standardize SLA setup time to under 30m', detail: 'CTO setup feedback highlights dashboard satisfaction.', status: 'Learning' },
    ]
  }
}
