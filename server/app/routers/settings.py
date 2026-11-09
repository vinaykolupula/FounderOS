"""
AI Models & Settings Router Module
Powered by Universal LLM Connectors & Dynamic Provider Registry.

Provides endpoints for managing AI provider credentials, custom base URLs, and active model selection:
1. Listing configured and supported AI providers (Anthropic, OpenAI, Gemini, DeepSeek, Groq, xAI Grok, OpenRouter, Ollama, Custom).
2. Live Auto-Discovery of available models via GET /v1/models.
3. Saving model selections, custom base URLs, and Vault-encrypting API keys.
4. Performing live health-check latency tests against selected AI models.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from app.db import get_async_session
from app.auth import get_current_workspace
from app.models import Workspace, AIProviderSetting, AuditLog
from app.vault import encrypt_token, decrypt_token
from app.services.llm_connectors import LLMProviderRegistry

router = APIRouter(prefix="/api/settings/models", tags=["AI Models & Provider Settings"])


class ModelSettingSchema(BaseModel):
    providerName: str = Field(..., max_length=50)
    selectedModel: str = Field(..., max_length=150)
    apiKey: Optional[str] = Field(None, max_length=500)
    customBaseUrl: Optional[str] = Field(None, max_length=500)
    reasoningEffort: Optional[str] = Field("high", max_length=20)
    isActive: bool = False


class ModelDiscoverSchema(BaseModel):
    providerName: str = Field(..., max_length=50)
    apiKey: Optional[str] = Field(None, max_length=500)
    customBaseUrl: Optional[str] = Field(None, max_length=500)


@router.get("")
async def get_model_settings(
    session: AsyncSession = Depends(get_async_session),
    workspace: Workspace = Depends(get_current_workspace)
):
    """Returns configured AI providers and full supported providers metadata catalog."""
    if not workspace or workspace.id is None:
        raise HTTPException(status_code=404, detail="Workspace not found")

    settings_res = await session.execute(
        select(AIProviderSetting).where(AIProviderSetting.workspace_id == workspace.id)
    )
    providers = settings_res.scalars().all()

    # Mask API key for security
    def mask_key(enc_key: Optional[str]) -> str:
        if not enc_key:
            return ""
        dec = decrypt_token(enc_key)
        if len(dec) > 8:
            return f"{dec[:4]}...{dec[-4:]}"
        return "••••••••"

    configured = [
        {
            "id": p.id,
            "providerName": p.provider_name,
            "selectedModel": p.selected_model,
            "customBaseUrl": p.custom_base_url,
            "reasoningEffort": p.reasoning_effort or "high",
            "maskedApiKey": mask_key(p.encrypted_api_key),
            "hasKey": bool(p.encrypted_api_key),
            "isActive": p.is_active,
            "status": p.status
        }
        for p in providers
    ]

    return {
        "providers": configured,
        "supportedProviders": LLMProviderRegistry.get_supported_providers_metadata()
    }


@router.post("/discover")
async def discover_provider_models(
    payload: ModelDiscoverSchema,
    session: AsyncSession = Depends(get_async_session),
    workspace: Workspace = Depends(get_current_workspace)
):
    """Dynamically queries the provider's live /v1/models endpoint to fetch active models."""
    api_key = payload.apiKey
    if not api_key:
        if workspace and workspace.id is not None:
            p_res = await session.execute(
                select(AIProviderSetting).where(
                    AIProviderSetting.workspace_id == workspace.id,
                    AIProviderSetting.provider_name == payload.providerName
                )
            )
            provider = p_res.scalars().first()
            if provider and provider.encrypted_api_key:
                api_key = decrypt_token(provider.encrypted_api_key)

    models = await LLMProviderRegistry.discover_models_live(
        provider_name=payload.providerName,
        api_key=api_key or "",
        custom_base_url=payload.customBaseUrl
    )
    return {"provider": payload.providerName, "models": models, "count": len(models)}


@router.post("")
async def save_model_setting(
    payload: ModelSettingSchema,
    session: AsyncSession = Depends(get_async_session),
    workspace: Workspace = Depends(get_current_workspace)
):
    """Saves AI provider settings, custom base URLs, and encrypts API key in Vault."""
    if not workspace or workspace.id is None:
        raise HTTPException(status_code=404, detail="Workspace not found")

    p_res = await session.execute(
        select(AIProviderSetting).where(
            AIProviderSetting.workspace_id == workspace.id,
            AIProviderSetting.provider_name == payload.providerName
        )
    )
    provider = p_res.scalars().first()

    # Encrypt API key if provided
    encrypted_key = encrypt_token(payload.apiKey) if payload.apiKey else (provider.encrypted_api_key if provider else None)

    if payload.isActive:
        # Deactivate all other providers
        all_res = await session.execute(
            select(AIProviderSetting).where(AIProviderSetting.workspace_id == workspace.id)
        )
        for p in all_res.scalars().all():
            p.is_active = False
            session.add(p)

    if not provider:
        provider = AIProviderSetting(
            workspace_id=workspace.id,
            provider_name=payload.providerName,
            selected_model=payload.selectedModel,
            encrypted_api_key=encrypted_key,
            custom_base_url=payload.customBaseUrl,
            reasoning_effort=payload.reasoningEffort or "high",
            is_active=payload.isActive,
            status="Connected" if (encrypted_key or payload.providerName in ["ollama", "custom"]) else "Not Configured"
        )
    else:
        provider.selected_model = payload.selectedModel
        provider.custom_base_url = payload.customBaseUrl
        provider.reasoning_effort = payload.reasoningEffort or "high"
        if payload.apiKey:
            provider.encrypted_api_key = encrypted_key
            provider.status = "Connected"
        provider.is_active = payload.isActive

    session.add(provider)

    assert workspace.id is not None
    audit = AuditLog(
        workspace_id=workspace.id,
        actor="founder",
        event="AI_MODEL_SETTINGS_UPDATED",
        details={
            "provider": payload.providerName,
            "model": payload.selectedModel,
            "customBaseUrl": payload.customBaseUrl,
            "reasoningEffort": payload.reasoningEffort or "high",
            "isActive": payload.isActive
        }
    )
    session.add(audit)

    await session.commit()
    return {"message": f"{payload.providerName.capitalize()} model settings saved successfully"}


@router.post("/test")
async def test_provider_connection(
    payload: ModelSettingSchema,
    session: AsyncSession = Depends(get_async_session),
    workspace: Workspace = Depends(get_current_workspace)
):
    """Tests provider connection live with latency measurement."""
    api_key = payload.apiKey
    custom_base_url = payload.customBaseUrl
    if not api_key:
        if workspace and workspace.id is not None:
            p_res = await session.execute(
                select(AIProviderSetting).where(
                    AIProviderSetting.workspace_id == workspace.id,
                    AIProviderSetting.provider_name == payload.providerName
                )
            )
            provider = p_res.scalars().first()
            if provider:
                if provider.encrypted_api_key:
                    api_key = decrypt_token(provider.encrypted_api_key)
                if not custom_base_url:
                    custom_base_url = provider.custom_base_url

    connector = LLMProviderRegistry.get_connector(payload.providerName)
    test_res = await connector.test_connection(
        model=payload.selectedModel,
        api_key=api_key or "",
        custom_base_url=custom_base_url
    )
    return test_res
