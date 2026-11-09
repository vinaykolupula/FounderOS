"""
FounderOS Universal LLM Connector & Dynamic Provider Registry
Hermes Agent (Nous Research), OpenClaw, and LiteLLM-grade multi-provider gateway.

Frontier Models Supported (2026 Intelligence Leaderboard):
- Anthropic: Claude Opus 5 (max), Claude Fable 5 (with fallback), Claude Sonnet 5, Claude 3.7 Sonnet
- OpenAI: GPT-5.6 Sol (max), GPT-5.6 Luna (max), o3-mini (high), o1 (high), gpt-4o
- xAI: Grok 4.6 (high/xhigh), Grok 4.5
- Moonshot AI: Kimi K3 (max 2.8T parameters, 1M context), Kimi K2.7 Code
- Google Gemini: Gemini 3.7 Flash (high), Gemini 3.6 Flash, Gemini 3.1 Pro, Gemini 2.0 Flash
- DeepSeek: DeepSeek V4 Pro 0813 (max), DeepSeek Reasoner (R1), DeepSeek Chat (V3)
- Zhipu AI / Z.ai: GLM-5.2 (max), GLM-5V-Turbo, GLM-4-Plus
- NVIDIA NIM: Nemotron 3 Ultra, Nemotron 3.5 Lightning, Llama-3.1 Nemotron 70B
- Meta / Muse: Muse Spark 1.2 (xhigh), Llama 3.3 70B
- Groq: Ultra-fast 500+ tok/s LPUs (Llama 3.3, DeepSeek R1 Distill)
- OpenRouter: 200+ frontier & open-weights models gateway
- Ollama: 100% private zero-data-leakage local execution
"""

import os
import json
import logging
import httpx
import asyncio
import time
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod

logger = logging.getLogger("founderos.llm.connectors")

_client_pool: Optional[httpx.AsyncClient] = None
_client_loop: Optional[asyncio.AbstractEventLoop] = None

def get_shared_client() -> httpx.AsyncClient:
    """Returns a pooled singleton httpx.AsyncClient configured with connection limits and keep-alive."""
    global _client_pool, _client_loop
    try:
        current_loop = asyncio.get_running_loop()
    except RuntimeError:
        current_loop = None

    if _client_pool is None or _client_pool.is_closed or (_client_loop is not None and _client_loop != current_loop):
        limits = httpx.Limits(max_keepalive_connections=20, max_connections=50, keepalive_expiry=30.0)
        _client_pool = httpx.AsyncClient(limits=limits, timeout=45.0)
        _client_loop = current_loop
    return _client_pool

async def close_shared_client():
    """Gracefully closes pooled connections upon application shutdown."""
    global _client_pool, _client_loop
    if _client_pool is not None and not _client_pool.is_closed:
        try:
            await _client_pool.aclose()
        except Exception:
            pass
        finally:
            _client_pool = None
            _client_loop = None


class BaseLLMConnector(ABC):
    """Abstract interface for all LLM provider connectors."""

    @abstractmethod
    async def generate_completion(
        self,
        prompt: str,
        system_instruction: str = "",
        model: str = "",
        api_key: str = "",
        custom_base_url: Optional[str] = None,
        temperature: float = 0.2,
        reasoning_effort: Optional[str] = None,
        timeout: float = 35.0
    ) -> str:
        """Executes completion request and returns generated text response."""
        pass

    @abstractmethod
    async def discover_models(
        self,
        api_key: str = "",
        custom_base_url: Optional[str] = None,
        timeout: float = 10.0
    ) -> List[str]:
        """Discovers all live models available on the provider account."""
        pass

    async def test_connection(
        self,
        model: str,
        api_key: str = "",
        custom_base_url: Optional[str] = None,
        timeout: float = 15.0
    ) -> Dict[str, Any]:
        """Tests live connectivity and measures response latency."""
        start = time.time()
        try:
            res = await self.generate_completion(
                prompt="Respond strictly with 'OK'",
                system_instruction="You are a health check assistant.",
                model=model,
                api_key=api_key,
                custom_base_url=custom_base_url,
                timeout=timeout
            )
            latency_ms = int((time.time() - start) * 1000)
            if res and len(res.strip()) > 0:
                return {
                    "success": True,
                    "status": f"Connected ✓ ({latency_ms}ms)",
                    "latency_ms": latency_ms,
                    "response": res.strip()[:100]
                }
            return {"success": False, "status": "Empty response from provider", "latency_ms": latency_ms}
        except Exception as e:
            latency_ms = int((time.time() - start) * 1000)
            return {"success": False, "status": f"Connection failed: {str(e)}", "latency_ms": latency_ms}


class OpenAICompatibleConnector(BaseLLMConnector):
    """
    Universal Connector for any OpenAI-compatible API:
    OpenAI, DeepSeek, Groq, xAI (Grok), Moonshot AI (Kimi), Zhipu AI (GLM / Z.ai),
    NVIDIA NIM, OpenRouter, Together AI, vLLM, LM Studio, etc.
    """

    def __init__(self, default_base_url: str, default_headers: Optional[Dict[str, str]] = None):
        self.default_base_url = default_base_url.rstrip("/")
        self.default_headers = default_headers or {}

    def _get_base_url(self, custom_base_url: Optional[str]) -> str:
        if custom_base_url and custom_base_url.strip():
            return custom_base_url.strip().rstrip("/")
        return self.default_base_url

    async def generate_completion(
        self,
        prompt: str,
        system_instruction: str = "",
        model: str = "",
        api_key: str = "",
        custom_base_url: Optional[str] = None,
        temperature: float = 0.2,
        reasoning_effort: Optional[str] = None,
        timeout: float = 35.0
    ) -> str:
        base_url = self._get_base_url(custom_base_url)
        headers = {"Content-Type": "application/json", **self.default_headers}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        payload: Dict[str, Any] = {
            "model": model or "gpt-5.6-sol",
            "messages": [
                {"role": "system", "content": system_instruction or "You are FounderOS executive AI."},
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature
        }

        # Cognitive Depth / Reasoning Effort Normalization
        effort = (reasoning_effort or "high").lower()
        if effort in ["max", "xhigh", "high", "medium", "low"]:
            # OpenAI, DeepSeek, Kimi, Grok, GLM reasoning models
            is_reasoning_model = any(k in model.lower() for k in ["o1", "o3", "reasoner", "sol", "luna", "k3", "grok", "v4", "glm-5", "nemotron"])
            if is_reasoning_model:
                payload["reasoning_effort"] = "high" if effort in ["max", "xhigh"] else effort
                # Reasoning models often require omit temperature or temperature 1.0
                if any(k in model.lower() for k in ["o1", "o3", "sol", "luna"]):
                    payload.pop("temperature", None)

        client = get_shared_client()
        endpoint = f"{base_url}/chat/completions" if not base_url.endswith("/chat/completions") else base_url
        res = await client.post(endpoint, headers=headers, json=payload, timeout=timeout)
        if res.status_code == 200:
            data = res.json()
            choices = data.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "")
        logger.warning(f"OpenAI-Compatible API error ({base_url}) {res.status_code}: {res.text}")
        return ""

    async def discover_models(
        self,
        api_key: str = "",
        custom_base_url: Optional[str] = None,
        timeout: float = 10.0
    ) -> List[str]:
        base_url = self._get_base_url(custom_base_url)
        headers = {"Content-Type": "application/json", **self.default_headers}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        endpoint = f"{base_url}/models" if not base_url.endswith("/models") else base_url
        try:
            client = get_shared_client()
            res = await client.get(endpoint, headers=headers, timeout=timeout)
            if res.status_code == 200:
                data = res.json()
                items = data.get("data", []) or data.get("models", [])
                models = []
                for item in items:
                    if isinstance(item, dict) and item.get("id"):
                        models.append(item.get("id"))
                    elif isinstance(item, dict) and item.get("name"):
                        models.append(item.get("name"))
                    elif isinstance(item, str):
                        models.append(item)
                if models:
                    return sorted(list(set(models)))
        except Exception as e:
            logger.warning(f"Failed to auto-discover models from {endpoint}: {e}")
        return []


class AnthropicConnector(BaseLLMConnector):
    """
    Dedicated Connector for Anthropic Claude:
    Claude Opus 5 (max), Claude Fable 5 (with fallback), Claude Sonnet 5, Claude 3.7 Sonnet.
    Supports extended thinking and hybrid reasoning effort.
    """

    def __init__(self, base_url: str = "https://api.anthropic.com/v1"):
        self.base_url = base_url.rstrip("/")

    def _resolve_model(self, model: str) -> str:
        m = (model or "claude-opus-5").lower()
        if "opus-5" in m or "opus 5" in m: return "claude-opus-5"
        if "fable-5" in m or "fable 5" in m: return "claude-fable-5"
        if "sonnet-5" in m or "sonnet 5" in m: return "claude-sonnet-5"
        if "3-7" in m or "3.7" in m: return "claude-3-7-sonnet-20250219"
        if "3-5" in m or "3.5" in m: return "claude-3-5-sonnet-20241022"
        return model

    async def generate_completion(
        self,
        prompt: str,
        system_instruction: str = "",
        model: str = "",
        api_key: str = "",
        custom_base_url: Optional[str] = None,
        temperature: float = 0.2,
        reasoning_effort: Optional[str] = None,
        timeout: float = 40.0
    ) -> str:
        base_url = (custom_base_url.strip().rstrip("/") if custom_base_url else self.base_url)
        canonical_model = self._resolve_model(model)

        headers = {
            "x-api-key": api_key or "",
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        payload: Dict[str, Any] = {
            "model": canonical_model,
            "max_tokens": 4096,
            "system": system_instruction or "You are FounderOS executive AI.",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature
        }

        # Cognitive Depth Thinking Budget (Anthropic Claude 5 / 3.7)
        effort = (reasoning_effort or "high").lower()
        if effort in ["max", "xhigh", "high", "medium"]:
            budget_tokens = 16384 if effort in ["max", "xhigh"] else (8192 if effort == "high" else 4096)
            payload["thinking"] = {"type": "enabled", "budget_tokens": budget_tokens}
            payload["max_tokens"] = budget_tokens + 4096
            payload.pop("temperature", None)  # Thinking mode requires default temperature

        client = get_shared_client()
        endpoint = f"{base_url}/messages"
        res = await client.post(endpoint, headers=headers, json=payload, timeout=timeout)
        if res.status_code == 200:
            data = res.json()
            content = data.get("content", [])
            text_parts = [c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") == "text"]
            return "".join(text_parts)
        
        # Fallback resilience (e.g. Claude Fable 5 with fallback or downgrade to Sonnet)
        if "fallback" in model.lower() or res.status_code in [429, 500, 503]:
            logger.warning(f"Anthropic model '{canonical_model}' failed ({res.status_code}), executing fallback to claude-sonnet-5...")
            payload["model"] = "claude-sonnet-5"
            payload.pop("thinking", None)
            fb_res = await client.post(endpoint, headers=headers, json=payload, timeout=timeout)
            if fb_res.status_code == 200:
                fb_data = fb_res.json()
                fb_content = fb_data.get("content", [])
                return "".join([c.get("text", "") for c in fb_content if isinstance(c, dict) and c.get("type") == "text"])

        logger.warning(f"Anthropic API error {res.status_code}: {res.text}")
        return ""

    async def discover_models(
        self,
        api_key: str = "",
        custom_base_url: Optional[str] = None,
        timeout: float = 10.0
    ) -> List[str]:
        base_url = (custom_base_url.strip().rstrip("/") if custom_base_url else self.base_url)
        headers = {
            "x-api-key": api_key or "",
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        try:
            client = get_shared_client()
            res = await client.get(f"{base_url}/models", headers=headers, timeout=timeout)
            if res.status_code == 200:
                data = res.json()
                items = data.get("data", [])
                models = [item.get("id") for item in items if isinstance(item, dict) and item.get("id")]
                if models:
                    return sorted(list(set(models)))
        except Exception as e:
            logger.warning(f"Anthropic model discovery failed: {e}")

        return [
            "claude-opus-5",
            "claude-fable-5",
            "claude-sonnet-5",
            "claude-3-7-sonnet-latest",
            "claude-3-5-sonnet-latest",
            "claude-3-5-haiku-latest"
        ]


class GeminiConnector(BaseLLMConnector):
    """
    Dedicated Connector for Google Gemini:
    Gemini 3.7 Flash (high), Gemini 3.6 Flash, Gemini 3.1 Pro, Gemini 2.0 Flash.
    """

    def __init__(self, base_url: str = "https://generativelanguage.googleapis.com/v1beta"):
        self.base_url = base_url.rstrip("/")

    async def generate_completion(
        self,
        prompt: str,
        system_instruction: str = "",
        model: str = "",
        api_key: str = "",
        custom_base_url: Optional[str] = None,
        temperature: float = 0.2,
        reasoning_effort: Optional[str] = None,
        timeout: float = 35.0
    ) -> str:
        base_url = (custom_base_url.strip().rstrip("/") if custom_base_url else self.base_url)
        model_id = model or "gemini-3.7-flash"

        url = f"{base_url}/models/{model_id}:generateContent"
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["x-goog-api-key"] = api_key

        payload: Dict[str, Any] = {
            "contents": [{"parts": [{"text": f"{system_instruction}\n\nUser Prompt: {prompt}"}]}],
            "generationConfig": {"temperature": temperature}
        }

        # Gemini Thinking / Cognitive Depth
        effort = (reasoning_effort or "high").lower()
        if effort in ["max", "xhigh", "high"]:
            payload["generationConfig"]["thinkingConfig"] = {"thinkingBudget": 8192 if effort in ["max", "xhigh"] else 4096}

        client = get_shared_client()
        res = await client.post(url, headers=headers, json=payload, timeout=timeout)
        if res.status_code == 200:
            data = res.json()
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    return parts[0].get("text", "")
        logger.warning(f"Gemini API error {res.status_code}: {res.text}")
        return ""

    async def discover_models(
        self,
        api_key: str = "",
        custom_base_url: Optional[str] = None,
        timeout: float = 10.0
    ) -> List[str]:
        base_url = (custom_base_url.strip().rstrip("/") if custom_base_url else self.base_url)
        if not api_key:
            return ["gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.1-pro", "gemini-2.0-flash"]

        url = f"{base_url}/models"
        headers = {"x-goog-api-key": api_key}
        try:
            client = get_shared_client()
            res = await client.get(url, headers=headers, timeout=timeout)
            if res.status_code == 200:
                data = res.json()
                models = []
                for m in data.get("models", []):
                    name = m.get("name", "").replace("models/", "")
                    if "generateContent" in m.get("supportedGenerationMethods", []):
                        models.append(name)
                if models:
                    return sorted(list(set(models)))
        except Exception as e:
            logger.warning(f"Gemini model discovery failed: {e}")

        return ["gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.1-pro", "gemini-2.0-flash"]


class OllamaConnector(BaseLLMConnector):
    """
    Dedicated Connector for Local Ollama / Private Offline LLMs.
    """

    def __init__(self, default_base_url: str = "http://127.0.0.1:11434"):
        self.default_base_url = default_base_url.rstrip("/")

    def _get_base_url(self, custom_base_url: Optional[str]) -> str:
        if custom_base_url and custom_base_url.strip():
            return custom_base_url.strip().rstrip("/")
        return self.default_base_url

    async def generate_completion(
        self,
        prompt: str,
        system_instruction: str = "",
        model: str = "",
        api_key: str = "",
        custom_base_url: Optional[str] = None,
        temperature: float = 0.2,
        reasoning_effort: Optional[str] = None,
        timeout: float = 45.0
    ) -> str:
        base_url = self._get_base_url(custom_base_url)
        model_id = model or "deepseek-r1:latest"

        client = get_shared_client()
        res = await client.post(
            f"{base_url}/api/generate",
            json={
                "model": model_id,
                "prompt": f"{system_instruction}\n\nUser Prompt: {prompt}",
                "stream": False,
                "options": {"temperature": temperature}
            },
            timeout=timeout
        )
        if res.status_code == 200:
            return res.json().get("response", "")
        return ""

    async def discover_models(
        self,
        api_key: str = "",
        custom_base_url: Optional[str] = None,
        timeout: float = 5.0
    ) -> List[str]:
        base_url = self._get_base_url(custom_base_url)
        try:
            client = get_shared_client()
            res = await client.get(f"{base_url}/api/tags", timeout=timeout)
            if res.status_code == 200:
                data = res.json()
                models = [m.get("name") for m in data.get("models", []) if m.get("name")]
                if models:
                    return sorted(models)
        except Exception as e:
            logger.info(f"Local Ollama discovery offline ({base_url}): {e}")

        return ["deepseek-r1:latest", "llama3.3:latest", "llama3.2:latest", "qwen2.5:latest", "mistral-large:latest"]


class LLMProviderRegistry:
    """
    Central Provider Registry managing dynamic connector dispatch, live auto-discovery,
    cognitive depth reasoning effort, and fallback resolution across all 2026 frontier models.
    """

    _CONNECTORS: Dict[str, BaseLLMConnector] = {
        "anthropic": AnthropicConnector("https://api.anthropic.com/v1"),
        "openai": OpenAICompatibleConnector("https://api.openai.com/v1"),
        "xai": OpenAICompatibleConnector("https://api.x.ai/v1"),
        "kimi": OpenAICompatibleConnector("https://api.moonshot.ai/v1"),
        "gemini": GeminiConnector("https://generativelanguage.googleapis.com/v1beta"),
        "deepseek": OpenAICompatibleConnector("https://api.deepseek.com"),
        "zhipu": OpenAICompatibleConnector("https://open.bigmodel.cn/api/paas/v4"),
        "nvidia": OpenAICompatibleConnector("https://integrate.api.nvidia.com/v1"),
        "muse": OpenAICompatibleConnector("https://api.together.xyz/v1"),
        "groq": OpenAICompatibleConnector("https://api.groq.com/openai/v1"),
        "openrouter": OpenAICompatibleConnector(
            "https://openrouter.ai/api/v1",
            default_headers={"HTTP-Referer": "https://founderos.dev", "X-Title": "FounderOS"}
        ),
        "ollama": OllamaConnector("http://127.0.0.1:11434"),
        "custom": OpenAICompatibleConnector("http://localhost:8000/v1")
    }

    _METADATA: Dict[str, Dict[str, Any]] = {
        "anthropic": {
            "name": "anthropic",
            "label": "Anthropic Claude",
            "description": "Claude Opus 5 (max), Claude Fable 5 (with fallback), Claude Sonnet 5 — #1 in nuanced strategic architecture.",
            "defaultModel": "claude-opus-5",
            "defaultBaseUrl": "https://api.anthropic.com/v1",
            "supportsAutoDiscovery": True,
            "availableModels": [
                "claude-opus-5",
                "claude-fable-5",
                "claude-sonnet-5",
                "claude-3-7-sonnet-latest",
                "claude-3-5-sonnet-latest",
                "claude-3-5-haiku-latest"
            ]
        },
        "openai": {
            "name": "openai",
            "label": "OpenAI",
            "description": "GPT-5.6 Sol (max), GPT-5.6 Luna (max), o3-mini (high), o1 — Peak multi-step causal reasoning & math.",
            "defaultModel": "gpt-5.6-sol",
            "defaultBaseUrl": "https://api.openai.com/v1",
            "supportsAutoDiscovery": True,
            "availableModels": [
                "gpt-5.6-sol",
                "gpt-5.6-luna",
                "o3-mini",
                "o1",
                "gpt-4o",
                "chatgpt-4o-latest"
            ]
        },
        "xai": {
            "name": "xai",
            "label": "xAI (Grok)",
            "description": "Grok 4.6 (high/xhigh), Grok 4.5 — Uncensored contrarian debate & live real-time knowledge synthesis.",
            "defaultModel": "grok-4.6",
            "defaultBaseUrl": "https://api.x.ai/v1",
            "supportsAutoDiscovery": True,
            "availableModels": [
                "grok-4.6",
                "grok-4.5",
                "grok-2-latest"
            ]
        },
        "kimi": {
            "name": "kimi",
            "label": "Moonshot AI (Kimi)",
            "description": "Kimi K3 (max 2.8T parameters, 1M context), Kimi K2.7 Code — SOTA large-scale code & long-context synthesis.",
            "defaultModel": "kimi-k3",
            "defaultBaseUrl": "https://api.moonshot.ai/v1",
            "supportsAutoDiscovery": True,
            "availableModels": [
                "kimi-k3",
                "kimi-k2.7-code",
                "kimi-k2.6"
            ]
        },
        "gemini": {
            "name": "gemini",
            "label": "Google Gemini",
            "description": "Gemini 3.7 Flash (high), Gemini 3.6 Flash, Gemini 3.1 Pro — Multi-million token context ingestion & multimodal.",
            "defaultModel": "gemini-3.7-flash",
            "defaultBaseUrl": "https://generativelanguage.googleapis.com/v1beta",
            "supportsAutoDiscovery": True,
            "availableModels": [
                "gemini-3.7-flash",
                "gemini-3.6-flash",
                "gemini-3.1-pro",
                "gemini-2.0-flash",
                "gemini-1.5-pro"
            ]
        },
        "deepseek": {
            "name": "deepseek",
            "label": "DeepSeek",
            "description": "DeepSeek V4 Pro 0813 (max), DeepSeek Reasoner (R1), Chat (V3) — Frontier reasoning at 90% lower operational cost.",
            "defaultModel": "deepseek-v4-pro-0813",
            "defaultBaseUrl": "https://api.deepseek.com",
            "supportsAutoDiscovery": True,
            "availableModels": [
                "deepseek-v4-pro-0813",
                "deepseek-reasoner",
                "deepseek-chat"
            ]
        },
        "zhipu": {
            "name": "zhipu",
            "label": "Zhipu AI (GLM / Z.ai)",
            "description": "GLM-5.2 (max), GLM-5V-Turbo — 1M context multimodal reasoning & deep enterprise agent workflows.",
            "defaultModel": "glm-5.2",
            "defaultBaseUrl": "https://open.bigmodel.cn/api/paas/v4",
            "supportsAutoDiscovery": True,
            "availableModels": [
                "glm-5.2",
                "glm-5v-turbo",
                "glm-4-plus"
            ]
        },
        "nvidia": {
            "name": "nvidia",
            "label": "NVIDIA NIM",
            "description": "Nemotron 3 Ultra, Nemotron 3.5 Lightning — Ultra-optimized GPU inference microservices for complex tasks.",
            "defaultModel": "nvidia/nemotron-3-ultra",
            "defaultBaseUrl": "https://integrate.api.nvidia.com/v1",
            "supportsAutoDiscovery": True,
            "availableModels": [
                "nvidia/nemotron-3-ultra",
                "nvidia/nemotron-3.5-lightning-30b",
                "meta/llama-3.1-nemotron-70b-instruct"
            ]
        },
        "muse": {
            "name": "muse",
            "label": "Meta / Muse",
            "description": "Muse Spark 1.2 (xhigh), Llama 3.3 70B — Cutting-edge open-weights intelligence & creative reasoning.",
            "defaultModel": "muse-spark-1.2",
            "defaultBaseUrl": "https://api.together.xyz/v1",
            "supportsAutoDiscovery": True,
            "availableModels": [
                "muse-spark-1.2",
                "meta-llama/llama-3.3-70b-instruct"
            ]
        },
        "groq": {
            "name": "groq",
            "label": "Groq (Ultra-Fast LPUs)",
            "description": "Sub-second 500+ tok/s inference for instantaneous executive briefing and board debate.",
            "defaultModel": "llama-3.3-70b-versatile",
            "defaultBaseUrl": "https://api.groq.com/openai/v1",
            "supportsAutoDiscovery": True,
            "availableModels": [
                "llama-3.3-70b-versatile",
                "deepseek-r1-distill-llama-70b",
                "llama-3.1-8b-instant"
            ]
        },
        "openrouter": {
            "name": "openrouter",
            "label": "OpenRouter Gateway",
            "description": "Universal multi-model gateway granting instant access to 200+ frontier & open-weights models.",
            "defaultModel": "anthropic/claude-opus-5",
            "defaultBaseUrl": "https://openrouter.ai/api/v1",
            "supportsAutoDiscovery": True,
            "availableModels": [
                "anthropic/claude-opus-5",
                "openai/gpt-5.6-sol",
                "x-ai/grok-4.6",
                "moonshotai/kimi-k3",
                "deepseek/deepseek-v4-pro",
                "zhipu/glm-5.2",
                "nvidia/nemotron-3-ultra"
            ]
        },
        "ollama": {
            "name": "ollama",
            "label": "Ollama / Local LLM",
            "description": "100% private, zero-data-leakage inference running locally on your hardware.",
            "defaultModel": "deepseek-r1:latest",
            "defaultBaseUrl": "http://127.0.0.1:11434",
            "supportsAutoDiscovery": True,
            "availableModels": [
                "deepseek-r1:latest",
                "llama3.3:latest",
                "qwen2.5:latest",
                "phi4:latest"
            ]
        },
        "custom": {
            "name": "custom",
            "label": "Custom OpenAI-Compatible",
            "description": "Connect to any self-hosted vLLM, LM Studio, TGI, or custom private endpoint.",
            "defaultModel": "default",
            "defaultBaseUrl": "http://localhost:8000/v1",
            "supportsAutoDiscovery": True,
            "availableModels": ["default"]
        }
    }

    @classmethod
    def get_connector(cls, provider_name: str) -> BaseLLMConnector:
        return cls._CONNECTORS.get(provider_name.lower(), cls._CONNECTORS["custom"])

    @classmethod
    def get_supported_providers_metadata(cls) -> List[Dict[str, Any]]:
        return list(cls._METADATA.values())

    @classmethod
    async def discover_models_live(
        cls,
        provider_name: str,
        api_key: str = "",
        custom_base_url: Optional[str] = None
    ) -> List[str]:
        connector = cls.get_connector(provider_name)
        discovered = await connector.discover_models(api_key=api_key, custom_base_url=custom_base_url)
        if not discovered:
            meta = cls._METADATA.get(provider_name.lower(), {})
            return meta.get("availableModels", ["default"])
        return discovered
