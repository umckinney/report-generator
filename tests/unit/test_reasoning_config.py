"""
Unit tests for reasoning configuration.
"""

import os
from unittest.mock import patch

import pytest

from report_generator.reasoning.config import ReasoningConfig, get_config, reset_config


class TestReasoningConfig:
    """Tests for ReasoningConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = ReasoningConfig()

        assert config.is_enabled() is False
        assert config.provider == "anthropic"
        assert config.max_tokens == 2048
        assert config.temperature == 0.0

    def test_explicit_enabled(self):
        """Test explicit enabled parameter."""
        config = ReasoningConfig(enabled=True)
        assert config.is_enabled() is True

        config = ReasoningConfig(enabled=False)
        assert config.is_enabled() is False

    def test_enabled_from_env_true(self):
        """Test reading enabled flag from environment (true values)."""
        for value in ["true", "1", "yes", "on", "TRUE", "ON"]:
            with patch.dict(os.environ, {"ENABLE_REASONING": value}):
                config = ReasoningConfig()
                assert config.is_enabled() is True

    def test_enabled_from_env_false(self):
        """Test reading enabled flag from environment (false values)."""
        for value in ["false", "0", "no", "off", "FALSE", "OFF"]:
            with patch.dict(os.environ, {"ENABLE_REASONING": value}):
                config = ReasoningConfig()
                assert config.is_enabled() is False

    def test_enabled_from_env_invalid(self):
        """Test that invalid env values use default."""
        with patch.dict(os.environ, {"ENABLE_REASONING": "maybe"}):
            config = ReasoningConfig()
            assert config.is_enabled() is False  # Default

    def test_provider_selection(self):
        """Test provider selection."""
        config = ReasoningConfig(provider="openai")
        assert config.get_provider_name() == "openai"

    def test_provider_from_env(self):
        """Test provider selection from environment."""
        with patch.dict(os.environ, {"REASONING_PROVIDER": "openai"}):
            config = ReasoningConfig()
            assert config.get_provider_name() == "openai"

    def test_max_tokens_explicit(self):
        """Test explicit max_tokens parameter."""
        config = ReasoningConfig(max_tokens=1000)
        assert config.max_tokens == 1000

    def test_max_tokens_from_env(self):
        """Test max_tokens from environment."""
        with patch.dict(os.environ, {"REASONING_MAX_TOKENS": "4096"}):
            config = ReasoningConfig()
            assert config.max_tokens == 4096

    def test_max_tokens_invalid_env(self):
        """Test that invalid max_tokens env uses default."""
        with patch.dict(os.environ, {"REASONING_MAX_TOKENS": "not-a-number"}):
            config = ReasoningConfig()
            assert config.max_tokens == 2048  # Default

    def test_temperature_explicit(self):
        """Test explicit temperature parameter."""
        config = ReasoningConfig(temperature=0.7)
        assert config.temperature == 0.7

    def test_temperature_from_env(self):
        """Test temperature from environment."""
        with patch.dict(os.environ, {"REASONING_TEMPERATURE": "0.5"}):
            config = ReasoningConfig()
            assert config.temperature == 0.5

    def test_temperature_invalid_env(self):
        """Test that invalid temperature env uses default."""
        with patch.dict(os.environ, {"REASONING_TEMPERATURE": "high"}):
            config = ReasoningConfig()
            assert config.temperature == 0.0  # Default

    def test_get_provider_disabled(self):
        """Test that get_provider raises error when disabled."""
        config = ReasoningConfig(enabled=False)

        with pytest.raises(ValueError, match="Reasoning layer is not enabled"):
            config.get_provider()

    def test_get_provider_anthropic(self):
        """Test getting Anthropic provider."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            with patch("anthropic.Anthropic"):
                config = ReasoningConfig(enabled=True, provider="anthropic")
                provider = config.get_provider()

                from report_generator.reasoning.provider import AnthropicProvider

                assert isinstance(provider, AnthropicProvider)

    def test_get_provider_unsupported(self):
        """Test that unsupported provider raises error."""
        config = ReasoningConfig(enabled=True, provider="unsupported-llm")

        with pytest.raises(ValueError, match="Unsupported LLM provider"):
            config.get_provider()

    def test_get_generation_params(self):
        """Test getting generation parameters."""
        config = ReasoningConfig(max_tokens=1500, temperature=0.3)
        params = config.get_generation_params()

        assert params == {"max_tokens": 1500, "temperature": 0.3}


class TestGlobalConfig:
    """Tests for global config management."""

    def teardown_method(self):
        """Reset global config after each test."""
        reset_config()

    def test_get_config_default(self):
        """Test that get_config returns default config."""
        config = get_config()
        assert isinstance(config, ReasoningConfig)
        assert config.is_enabled() is False

    def test_get_config_singleton(self):
        """Test that get_config returns same instance."""
        config1 = get_config()
        config2 = get_config()
        assert config1 is config2

    def test_set_config(self):
        """Test setting global config."""
        from report_generator.reasoning.config import set_config

        custom_config = ReasoningConfig(enabled=True, max_tokens=3000)
        set_config(custom_config)

        retrieved_config = get_config()
        assert retrieved_config is custom_config
        assert retrieved_config.is_enabled() is True
        assert retrieved_config.max_tokens == 3000

    def test_reset_config(self):
        """Test resetting global config."""
        # Set custom config
        custom_config = ReasoningConfig(enabled=True)
        from report_generator.reasoning.config import set_config

        set_config(custom_config)
        assert get_config().is_enabled() is True

        # Reset
        reset_config()
        new_config = get_config()
        assert new_config is not custom_config
        assert new_config.is_enabled() is False
