import unittest
import asyncio
from app.services.llm_connectors import (
    LLMProviderRegistry,
    OpenAICompatibleConnector,
    AnthropicConnector,
    GeminiConnector,
    OllamaConnector,
    BaseLLMConnector
)


class TestLLMConnectors(unittest.IsolatedAsyncioTestCase):
    """Function-to-function tests for Hermes & OpenClaw style Universal LLM Connectors."""

    def test_registry_provider_lookup(self):
        providers = ["anthropic", "openai", "xai", "kimi", "gemini", "deepseek", "zhipu", "nvidia", "muse", "groq", "openrouter", "ollama", "custom"]
        for p in providers:
            connector = LLMProviderRegistry.get_connector(p)
            self.assertIsInstance(connector, BaseLLMConnector, f"Provider {p} should return a valid BaseLLMConnector")

    def test_unknown_provider_defaults_to_custom(self):
        connector = LLMProviderRegistry.get_connector("some_unknown_local_inference")
        self.assertIsInstance(connector, OpenAICompatibleConnector)

    def test_supported_providers_metadata_catalog(self):
        metadata = LLMProviderRegistry.get_supported_providers_metadata()
        self.assertIsInstance(metadata, list)
        self.assertGreaterEqual(len(metadata), 12)
        names = [item["name"] for item in metadata]
        self.assertIn("anthropic", names)
        self.assertIn("openai", names)
        self.assertIn("kimi", names)
        self.assertIn("gemini", names)
        self.assertIn("deepseek", names)
        self.assertIn("zhipu", names)
        self.assertIn("nvidia", names)
        self.assertIn("muse", names)

    def test_anthropic_model_canonicalization(self):
        connector = LLMProviderRegistry.get_connector("anthropic")
        self.assertIsInstance(connector, AnthropicConnector)
        self.assertEqual(connector._resolve_model("claude-opus-5"), "claude-opus-5")
        self.assertEqual(connector._resolve_model("claude-fable-5"), "claude-fable-5")
        self.assertEqual(connector._resolve_model("claude-3-7-sonnet-latest"), "claude-3-7-sonnet-20250219")
        self.assertEqual(connector._resolve_model("claude-3-5-sonnet-latest"), "claude-3-5-sonnet-20241022")

    def test_openai_compatible_base_url_resolution(self):
        connector = OpenAICompatibleConnector(default_base_url="https://api.openai.com/v1")
        self.assertEqual(connector._get_base_url(None), "https://api.openai.com/v1")
        self.assertEqual(connector._get_base_url(""), "https://api.openai.com/v1")
        self.assertEqual(connector._get_base_url("http://localhost:8000/v1/"), "http://localhost:8000/v1")

    def test_ollama_base_url_resolution(self):
        connector = OllamaConnector(default_base_url="http://127.0.0.1:11434")
        self.assertEqual(connector._get_base_url(None), "http://127.0.0.1:11434")
        self.assertEqual(connector._get_base_url("http://192.168.1.100:11434/"), "http://192.168.1.100:11434")

    async def test_discover_models_fallback_when_offline(self):
        models = await LLMProviderRegistry.discover_models_live("anthropic", api_key="")
        self.assertIsInstance(models, list)
        self.assertIn("claude-opus-5", models)

        gemini_models = await LLMProviderRegistry.discover_models_live("gemini", api_key="")
        self.assertIn("gemini-3.7-flash", gemini_models)


if __name__ == "__main__":
    unittest.main()
