"""
Configuration for LLM reasoning layer.

This module provides configuration management for the reasoning layer,
including feature flags, model selection, and reasoning parameters.
"""

import os
from typing import Optional


class ReasoningConfig:
    """
    Configuration for LLM reasoning layer.

    This class manages feature flags and parameters for the reasoning layer.
    Settings can be controlled via environment variables or code.

    Environment Variables:
        ENABLE_REASONING: Enable/disable reasoning layer (true/false)
        REASONING_PROVIDER: LLM provider to use (anthropic, openai, etc.)
        REASONING_MAX_TOKENS: Default max tokens for generation
        REASONING_TEMPERATURE: Default temperature for generation

    Example:
        >>> config = ReasoningConfig()
        >>> if config.is_enabled():
        ...     provider = config.get_provider()
        ...     result = provider.generate("...")
    """

    # Default values
    DEFAULT_MAX_TOKENS = 2048
    DEFAULT_TEMPERATURE = 0.0
    DEFAULT_PROVIDER = "anthropic"

    def __init__(
        self,
        enabled: Optional[bool] = None,
        provider: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ):
        """
        Initialize reasoning configuration.

        Args:
            enabled: Enable reasoning layer (if None, reads from ENABLE_REASONING env)
            provider: LLM provider name (if None, reads from REASONING_PROVIDER env)
            max_tokens: Default max tokens (if None, reads from REASONING_MAX_TOKENS env)
            temperature: Default temperature (if None, reads from REASONING_TEMPERATURE env)
        """
        # Feature flag
        self.enabled = self._parse_bool_env("ENABLE_REASONING", enabled, default=False)

        # Provider selection
        self.provider = (
            provider
            or os.getenv("REASONING_PROVIDER", self.DEFAULT_PROVIDER).lower()
        )

        # Generation parameters
        self.max_tokens = self._parse_int_env(
            "REASONING_MAX_TOKENS", max_tokens, default=self.DEFAULT_MAX_TOKENS
        )

        self.temperature = self._parse_float_env(
            "REASONING_TEMPERATURE", temperature, default=self.DEFAULT_TEMPERATURE
        )

    def is_enabled(self) -> bool:
        """
        Check if reasoning layer is enabled.

        Returns:
            True if reasoning is enabled, False otherwise
        """
        return self.enabled

    def get_provider_name(self) -> str:
        """
        Get the configured provider name.

        Returns:
            Provider name (e.g., 'anthropic', 'openai')
        """
        return self.provider

    def get_provider(self):
        """
        Get an initialized LLM provider instance.

        Returns:
            LLMProvider instance based on configuration

        Raises:
            ValueError: If provider is not supported or not configured
        """
        if not self.is_enabled():
            raise ValueError("Reasoning layer is not enabled")

        if self.provider == "anthropic":
            from report_generator.reasoning.provider import AnthropicProvider

            return AnthropicProvider()

        elif self.provider == "openai":
            from report_generator.reasoning.provider import OpenAIProvider

            return OpenAIProvider()

        else:
            raise ValueError(
                f"Unsupported LLM provider: {self.provider}. "
                f"Supported providers: anthropic, openai"
            )

    def get_generation_params(self) -> dict:
        """
        Get default generation parameters.

        Returns:
            Dictionary with max_tokens and temperature
        """
        return {
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }

    @staticmethod
    def _parse_bool_env(
        env_var: str, override: Optional[bool], default: bool
    ) -> bool:
        """Parse boolean from environment variable."""
        if override is not None:
            return override

        value = os.getenv(env_var, "").lower()
        if value in ("true", "1", "yes", "on"):
            return True
        elif value in ("false", "0", "no", "off"):
            return False
        else:
            return default

    @staticmethod
    def _parse_int_env(env_var: str, override: Optional[int], default: int) -> int:
        """Parse integer from environment variable."""
        if override is not None:
            return override

        value = os.getenv(env_var)
        if value:
            try:
                return int(value)
            except ValueError:
                return default
        return default

    @staticmethod
    def _parse_float_env(
        env_var: str, override: Optional[float], default: float
    ) -> float:
        """Parse float from environment variable."""
        if override is not None:
            return override

        value = os.getenv(env_var)
        if value:
            try:
                return float(value)
            except ValueError:
                return default
        return default


# Global config instance (can be overridden)
_global_config: Optional[ReasoningConfig] = None


def get_config() -> ReasoningConfig:
    """
    Get the global reasoning configuration.

    Returns:
        ReasoningConfig instance
    """
    global _global_config
    if _global_config is None:
        _global_config = ReasoningConfig()
    return _global_config


def set_config(config: ReasoningConfig) -> None:
    """
    Set the global reasoning configuration.

    Args:
        config: ReasoningConfig instance to use globally
    """
    global _global_config
    _global_config = config


def reset_config() -> None:
    """Reset global configuration to defaults."""
    global _global_config
    _global_config = None
