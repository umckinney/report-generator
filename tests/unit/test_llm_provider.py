"""
Unit tests for LLM provider implementations.

These tests use mocking to avoid actual API calls.
"""

import os
from unittest.mock import Mock, patch

import pytest

from report_generator.reasoning.provider import AnthropicProvider, LLMProviderError, OpenAIProvider


class TestAnthropicProvider:
    """Tests for AnthropicProvider."""

    def test_init_with_api_key(self):
        """Test initialization with explicit API key."""
        with patch("anthropic.Anthropic"):
            provider = AnthropicProvider(api_key="test-key-123")
            assert provider.api_key == "test-key-123"
            assert provider.model == AnthropicProvider.DEFAULT_MODEL

    def test_init_with_env_var(self):
        """Test initialization using environment variable."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "env-key-456"}):
            with patch("anthropic.Anthropic"):
                provider = AnthropicProvider()
                assert provider.api_key == "env-key-456"

    def test_init_missing_api_key(self):
        """Test that initialization fails without API key."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="API key is required"):
                AnthropicProvider()

    def test_init_custom_model(self):
        """Test initialization with custom model."""
        with patch("anthropic.Anthropic"):
            provider = AnthropicProvider(api_key="test-key", model="claude-opus-4")
            assert provider.model == "claude-opus-4"

    def test_generate_success(self):
        """Test successful text generation."""
        mock_response = Mock()
        mock_response.content = [Mock(text="Generated summary")]
        mock_response.usage = Mock(input_tokens=100, output_tokens=50)

        with patch("anthropic.Anthropic") as mock_anthropic:
            mock_client = Mock()
            mock_client.messages.create.return_value = mock_response
            mock_anthropic.return_value = mock_client

            provider = AnthropicProvider(api_key="test-key")
            result = provider.generate("Summarize this", max_tokens=500)

            assert result == "Generated summary"
            assert provider.get_token_usage() == {"input_tokens": 100, "output_tokens": 50}

    def test_generate_empty_prompt(self):
        """Test that empty prompt raises error."""
        with patch("anthropic.Anthropic"):
            provider = AnthropicProvider(api_key="test-key")
            with pytest.raises(ValueError, match="Prompt cannot be empty"):
                provider.generate("")

    def test_generate_invalid_max_tokens(self):
        """Test that invalid max_tokens raises error."""
        with patch("anthropic.Anthropic"):
            provider = AnthropicProvider(api_key="test-key")
            with pytest.raises(ValueError, match="max_tokens must be positive"):
                provider.generate("test", max_tokens=0)

    def test_generate_invalid_temperature(self):
        """Test that invalid temperature raises error."""
        with patch("anthropic.Anthropic"):
            provider = AnthropicProvider(api_key="test-key")
            with pytest.raises(ValueError, match="temperature must be between"):
                provider.generate("test", temperature=-0.1)

    def test_generate_with_retries(self):
        """Test that provider retries on transient failures."""
        mock_response = Mock()
        mock_response.content = [Mock(text="Success after retries")]
        mock_response.usage = Mock(input_tokens=100, output_tokens=50)

        with patch("anthropic.Anthropic") as mock_anthropic:
            mock_client = Mock()
            mock_client.messages.create.side_effect = [
                Exception("Network error"),
                Exception("Rate limit"),
                mock_response,
            ]
            mock_anthropic.return_value = mock_client

            with patch("time.sleep"):
                provider = AnthropicProvider(api_key="test-key", max_retries=3)
                result = provider.generate("test prompt")

                assert result == "Success after retries"
                assert mock_client.messages.create.call_count == 3

    def test_token_usage_accumulation(self):
        """Test that token usage accumulates."""
        responses = [
            Mock(content=[Mock(text="First")], usage=Mock(input_tokens=50, output_tokens=25)),
            Mock(content=[Mock(text="Second")], usage=Mock(input_tokens=75, output_tokens=30)),
        ]

        with patch("anthropic.Anthropic") as mock_anthropic:
            mock_client = Mock()
            mock_client.messages.create.side_effect = responses
            mock_anthropic.return_value = mock_client

            provider = AnthropicProvider(api_key="test-key")
            provider.generate("First")
            provider.generate("Second")

            usage = provider.get_token_usage()
            assert usage["input_tokens"] == 125
            assert usage["output_tokens"] == 55

    def test_reset_token_usage(self):
        """Test that token usage can be reset."""
        mock_response = Mock()
        mock_response.content = [Mock(text="Response")]
        mock_response.usage = Mock(input_tokens=100, output_tokens=50)

        with patch("anthropic.Anthropic") as mock_anthropic:
            mock_client = Mock()
            mock_client.messages.create.return_value = mock_response
            mock_anthropic.return_value = mock_client

            provider = AnthropicProvider(api_key="test-key")
            provider.generate("test")

            assert provider.get_token_usage()["input_tokens"] == 100

            provider.reset_token_usage()
            usage = provider.get_token_usage()
            assert usage["input_tokens"] == 0
            assert usage["output_tokens"] == 0


class TestOpenAIProvider:
    """Tests for OpenAI provider (placeholder)."""

    def test_not_implemented(self):
        """Test that OpenAI provider raises NotImplementedError."""
        with pytest.raises(NotImplementedError, match="not yet implemented"):
            OpenAIProvider(api_key="test-key")


class TestLLMProviderInterface:
    """Tests for the abstract LLMProvider interface."""

    def test_interface_methods_exist(self):
        """Test that required interface methods are defined."""
        from report_generator.reasoning.provider import LLMProvider

        required_methods = ["generate", "get_token_usage", "reset_token_usage"]

        for method in required_methods:
            assert hasattr(LLMProvider, method)
            assert callable(getattr(LLMProvider, method))
