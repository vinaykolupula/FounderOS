"""
FounderOS Database Schemas & SQLModel Domain Objects

This module defines all relational database models using SQLModel (SQLAlchemy + Pydantic).
Key Domain Objects:
- Workspace: Root container holding all company, founder, action, task, and AI settings state.
- FounderProfile: Personal DNA, superpower, capability gap, energy state, and comms preferences.
- CompanyProfile: Architecture parameters, burn rate, GTM motion, moat, tech stack, and financial constraints.
- Task: Prioritized founder tasks with delegation status and AI synthesis notes.
- ActionItem: Drafted approval-gated actions generated autonomously by the FounderOS agent.
- Decision: Institutional memory ledger storing strategic choices and outcomes.
- AIProviderSetting: Vault-encrypted API keys and active model preferences.
- Connector: Integration state (Slack, Linear, Gmail, HubSpot, Stripe) and OAuth token vault link.
- Evidence: Ingested signals and vector evidence for RAG dynamic briefing.
- AuditLog: Security and event audit trail recording all founder & AI agent actions.
"""

from datetime import datetime, timezone
from typing import Optional, List
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship, JSON


# ==========================================
# Workspace & Root Domain Model
# ==========================================

class WorkspaceBase(SQLModel):
    is_onboarded: bool = False


class Workspace(WorkspaceBase, table=True):
    """
    Root Workspace entity.
    Serves as the multi-tenant scope isolating company data, settings, and agent history.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationships
    company: Optional["CompanyProfile"] = Relationship(back_populates="workspace")
    founder: Optional["FounderProfile"] = Relationship(back_populates="workspace")
    connectors: List["Connector"] = Relationship(back_populates="workspace")
    actions: List["ActionItem"] = Relationship(back_populates="workspace")
    decisions: List["Decision"] = Relationship(back_populates="workspace")
    ai_settings: List["AIProviderSetting"] = Relationship(back_populates="workspace")
    tasks: List["Task"] = Relationship(back_populates="workspace")


# ==========================================
# Domain Enums for Strict Validation
# ==========================================

class BusinessModelEnum(str, Enum):
    B2B_SAAS = "B2B SaaS"
    B2C_D2C = "B2C / D2C"
    MARKETPLACE = "Marketplace"
    AGENCY_SERVICES = "Agency / Services"
    HARDWARE_MANUFACTURING = "Hardware / Manufacturing"
    OPEN_SOURCE = "Open Source"
    OTHER = "Other"

class PlatformFocusEnum(str, Enum):
    WEB_APP = "Web Application"
    MOBILE_APP = "Mobile App"
    API_DEV_TOOLS = "API / Developer Tools"
    CHROME_EXTENSION = "Chrome Extension"
    OFFLINE_RETAIL = "Offline / Retail"
    OTHER = "Other"

class FundingStateEnum(str, Enum):
    BOOTSTRAPPED = "Bootstrapped"
    PRE_SEED = "Pre-Seed"
    SEED = "Seed"
    SERIES_A = "Series A"
    SERIES_B_PLUS = "Series B+"
    PUBLIC = "Public"

class RevenueRangeEnum(str, Enum):
    PRE_REVENUE = "Pre-revenue"
    UNDER_10K_MRR = "<$10k MRR"
    TEN_TO_100K_MRR = "$10k-$100k MRR"
    OVER_1M_ARR = "$1M+ ARR"

class StageEnum(str, Enum):
    IDEA = "Idea stage"
    PRE_REVENUE = "Pre-revenue"
    EARLY_REVENUE = "Early revenue"
    GROWTH = "Growth stage"
    SCALE = "Scale"

class TeamSizeEnum(str, Enum):
    SOLO = "Solo founder"
    TWO_TO_FIVE = "2-5 people"
    SIX_TO_FIFTEEN = "6-15 people"
    SIXTEEN_TO_FIFTY = "16-50 people"
    FIFTY_PLUS = "50+ people"

class FounderRole(str, Enum):
    SOLO_FOUNDER = "Solo Founder"
    CEO = "CEO"
    CTO = "CTO"
    COO = "COO"
    OTHER = "Other"

class FounderBackground(str, Enum):
    TECHNICAL = "Engineering / Technical"
    PRODUCT = "Product / Design"
    SALES_GTM = "Sales / Go-to-Market"
    OPERATIONS = "Operations / Finance"
    MARKETING = "Marketing / Growth"

class ExperienceLevel(str, Enum):
    FIRST_TIME = "First-time Founder"
    SECOND_TIME = "Second-time Founder"
    SERIAL = "Serial Founder (3+)"
    INDUSTRY_VET = "Industry Veteran (10+ yrs)"

class FounderSuperpower(str, Enum):
    ENGINEERING = "Building & Engineering"
    SALES = "Sales & Closing Deals"
    PRODUCT = "Product Vision & UX"
    FUNDRAISING = "Fundraising & Capital"
    RECRUITING = "Recruiting & Team Building"


# ==========================================
# Founder Profile & Psychological DNA
# ==========================================

class FounderProfileBase(SQLModel):
    name: str = Field(..., max_length=255)
    role: FounderRole
    background: FounderBackground
    experience_level: ExperienceLevel
    domain_expertise: str = Field(..., max_length=500)
    superpower: FounderSuperpower
    primary_gap: FounderSuperpower
    learning_focus: str = Field(..., max_length=500)
    
    # Deep Founder Harness Context (Injected into agent prompts)
    communication_style: str = Field(default="Direct and brief", max_length=255)
    energy_state: str = Field(default="Steady pace", max_length=255)
    core_values: str = Field(default="Speed, Customer Obsession", max_length=500)


class FounderProfile(FounderProfileBase, table=True):
    """Stores the founder's DNA, strengths, gaps, and communication style preferences."""
    id: Optional[int] = Field(default=None, primary_key=True)
    workspace_id: int = Field(foreign_key="workspace.id", index=True)
    workspace: Optional[Workspace] = Relationship(back_populates="founder")


# ==========================================
# Company Profile & Architecture Harness
# ==========================================

class CompanyProfileBase(SQLModel):
    name: str
    
    website_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    social_url: Optional[str] = None
    
    business_model: Optional[BusinessModelEnum] = None
    platform_focus: Optional[PlatformFocusEnum] = None
    funding_state: Optional[FundingStateEnum] = None
    revenue_range: Optional[RevenueRangeEnum] = None
    
    stage: StageEnum
    team_size: TeamSizeEnum
    ideal_customer: str
    objective: str
    primary_metric: str
    primary_constraint: str
    runway_months: int = Field(default=12, ge=0)

    # Deep Company Harness Context (Injected into Executive Debate & Execution)
    burn_rate: str = Field(default="Unknown", max_length=100)
    gtm_motion: str = Field(default="Product-Led Growth", max_length=100)
    tech_stack: str = Field(default="React, Node.js, Postgres", max_length=500)
    competitive_moat: str = Field(default="First mover advantage", max_length=500)


class CompanyProfile(CompanyProfileBase, table=True):
    """Stores company architecture, financials, moat, tech stack, and primary constraints."""
    id: Optional[int] = Field(default=None, primary_key=True)
    workspace_id: int = Field(foreign_key="workspace.id", index=True)

    workspace: Optional[Workspace] = Relationship(back_populates="company")


# ==========================================
# System Connectors & Integration Vault
# ==========================================

class ConnectorBase(SQLModel):
    connector_id: str  # 'gmail' | 'slack' | 'linear' | 'hubspot' | 'stripe'
    name: str
    description: str
    category: str
    status: str = "not_connected"  # 'not_connected' | 'configured'
    encrypted_oauth_token: Optional[str] = None


class Connector(ConnectorBase, table=True):
    """Tracks connected external tools and encrypted OAuth credentials in Vault."""
    id: Optional[int] = Field(default=None, primary_key=True)
    workspace_id: int = Field(foreign_key="workspace.id", index=True)

    workspace: Optional[Workspace] = Relationship(back_populates="connectors")


# ==========================================
# Approval-Gated Action Queue
# ==========================================

class ActionItemBase(SQLModel):
    title: str
    detail: str
    source: str
    status: str = "Ready"  # 'Ready' | 'Draft' | 'Approved' | 'Executed'
    action_type: Optional[str] = None
    payload: Optional[dict] = Field(default=None, sa_type=JSON)


class ActionItem(ActionItemBase, table=True):
    """Approval-gated execution receipts drafted autonomously by the FounderOS agent."""
    id: Optional[int] = Field(default=None, primary_key=True)
    workspace_id: int = Field(foreign_key="workspace.id", index=True)

    workspace: Optional[Workspace] = Relationship(back_populates="actions")


# ==========================================
# Institutional Decision Ledger
# ==========================================

class DecisionBase(SQLModel):
    decision_code: str  # e.g. '#024'
    title: str
    detail: str
    status: str = "Open"  # 'Open' | 'Validated' | 'Learning'
    review_date: Optional[datetime] = None
    outcome: Optional[str] = None


class Decision(DecisionBase, table=True):
    """Institutional memory ledger recording key strategic choices and post-mortem outcomes."""
    id: Optional[int] = Field(default=None, primary_key=True)
    workspace_id: int = Field(foreign_key="workspace.id", index=True)

    workspace: Optional[Workspace] = Relationship(back_populates="decisions")


# ==========================================
# Vector Evidence & Signal Ingestion
# ==========================================

class EvidenceBase(SQLModel):
    source_provider: str  # 'gmail' | 'linear' | 'hubspot'
    external_id: Optional[str] = None
    title: str
    content: str
    trust_level: str = "verified_signal"
    provenance: Optional[str] = None


class Evidence(EvidenceBase, table=True):
    """Ingested external evidence chunks vector-indexed for daily CEO briefing RAG."""
    id: Optional[int] = Field(default=None, primary_key=True)
    workspace_id: int = Field(foreign_key="workspace.id", index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ==========================================
# Security Audit Trail
# ==========================================

class AuditLogBase(SQLModel):
    actor: str  # 'founder' | 'founderos_agent' | 'system'
    event: str
    details: Optional[dict] = Field(default=None, sa_type=JSON)


class AuditLog(AuditLogBase, table=True):
    """Immutable audit trail logging founder approvals, setting changes, and agent actions."""
    id: Optional[int] = Field(default=None, primary_key=True)
    workspace_id: int = Field(foreign_key="workspace.id", index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ==========================================
# Vault Encrypted AI Provider Settings
# ==========================================

class AIProviderSettingBase(SQLModel):
    provider_name: str  # 'anthropic' | 'openai' | 'xai' | 'kimi' | 'gemini' | 'deepseek' | 'zhipu' | 'nvidia' | 'muse' | 'groq' | 'openrouter' | 'ollama' | 'custom'
    selected_model: str  # e.g. 'claude-opus-5', 'gpt-5.6-sol', 'grok-4.6', 'kimi-k3', 'gemini-3.7-flash', 'deepseek-v4-pro-0813', 'glm-5.2'
    encrypted_api_key: Optional[str] = None
    custom_base_url: Optional[str] = None
    reasoning_effort: Optional[str] = "high"  # 'max' | 'xhigh' | 'high' | 'medium' | 'low' | 'off'
    is_active: bool = False
    status: str = "Not Configured"  # 'Connected' | 'Not Configured' | 'Invalid Key'


class AIProviderSetting(AIProviderSettingBase, table=True):
    """Stores AI Provider model selections and AES-encrypted API keys."""
    id: Optional[int] = Field(default=None, primary_key=True)
    workspace_id: int = Field(foreign_key="workspace.id", index=True)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    workspace: Optional[Workspace] = Relationship(back_populates="ai_settings")


# ==========================================
# Task Management & Agent Execution Queue
# ==========================================

class TaskBase(SQLModel):
    title: str
    description: Optional[str] = None
    priority: str = "P1_HIGH"  # 'P0_CRITICAL' | 'P1_HIGH' | 'P2_MEDIUM' | 'P3_LOW'
    category: str = "TODAY"  # 'TODAY' | 'UPCOMING' | 'DELEGATED'
    source: str = "AGENT_MONITOR"  # 'EMAIL' | 'CALENDAR' | 'LINEAR' | 'FOUNDER_MANUAL' | 'AGENT_MONITOR'
    status: str = "PENDING"  # 'PENDING' | 'IN_PROGRESS' | 'DELEGATED' | 'COMPLETED' | 'FAILED'
    due_date: Optional[str] = "Today"
    agent_note: Optional[str] = None


class Task(TaskBase, table=True):
    """Operational tasks prioritized by urgency and monitored/executed by the AI agent."""
    id: Optional[int] = Field(default=None, primary_key=True)
    workspace_id: int = Field(foreign_key="workspace.id", index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    workspace: Optional[Workspace] = Relationship(back_populates="tasks")
