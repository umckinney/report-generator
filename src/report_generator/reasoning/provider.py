"""
LLM provider interface and implementations.

This module defines an abstract LLM provider interface and concrete implementations
for different LLM services (Anthropic Claude, OpenAI, etc.). The abstraction allows
easy switching between providers without changing downstream code.
"""

import os
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class LLMProvider(ABC):
    """
    Abstract interface for LLM providers.

    This interface allows the Chief of Staff Agent to work with multiple
    LLM providers (Anthropic, OpenAI, local models, etc.) without tight coupling.

    Implementers should handle:
    - API authentication
    - Request/response formatting
    - Error handling and retries
    - Rate limiting
    - Token usage tracking
    """

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.0,
    ) -> str:
        """
        Generate text from a prompt.

        Args:
            prompt: The user prompt to send to the LLM
            system_prompt: Optional system prompt (context/instructions)
            max_tokens: Maximum tokens to generate in response
            temperature: Sampling temperature (0.0 = deterministic, 1.0 = creative)

        Returns:
            Generated text as a string

        Raises:
            LLMProviderError: If the API call fails after retries
            ValueError: If parameters are invalid
        """
        pass

    @abstractmethod
    def get_token_usage(self) -> Dict[str, int]:
        """
        Get cumulative token usage statistics.

        Returns:
            Dictionary with 'input_tokens' and 'output_tokens' counts
        """
        pass

    @abstractmethod
    def reset_token_usage(self) -> None:
        """Reset token usage counters to zero."""
        pass


class LLMProviderError(Exception):
    """Exception raised when LLM provider API calls fail."""

    pass


class AnthropicProvider(LLMProvider):
    """
    Anthropic Claude API provider.

    This implementation uses the Anthropic Python SDK to interact with Claude models.

    Environment variables:
        ANTHROPIC_API_KEY: Required API key for authentication
        ANTHROPIC_MODEL: Optional model override (default: claude-sonnet-4-5-20250929)

    Example:
        >>> provider = AnthropicProvider()
        >>> response = provider.generate("Summarize this data: ...", max_tokens=500)
        >>> print(provider.get_token_usage())
        {'input_tokens': 150, 'output_tokens': 200}
    """

    DEFAULT_MODEL = "claude-sonnet-4-5-20250929"
    MAX_RETRIES = 3
    RETRY_DELAY = 1.0  # seconds

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        max_retries: int = MAX_RETRIES,
    ):
        """
        Initialize Anthropic provider.

        Args:
            api_key: Anthropic API key (if None, reads from ANTHROPIC_API_KEY env var)
            model: Model ID to use (if None, uses DEFAULT_MODEL or ANTHROPIC_MODEL env var)
            max_retries: Maximum number of retry attempts for failed requests

        Raises:
            ValueError: If API key is not provided and not in environment
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Anthropic API key is required. Set ANTHROPIC_API_KEY environment "
                "variable or pass api_key parameter."
            )

        self.model = model or os.getenv("ANTHROPIC_MODEL", self.DEFAULT_MODEL)
        self.max_retries = max_retries

        # Token usage tracking
        self._input_tokens = 0
        self._output_tokens = 0

        # Lazy import to avoid requiring anthropic package if not using this provider
        try:
            import anthropic

            self.client = anthropic.Anthropic(api_key=self.api_key)
        except ImportError as e:
            raise ImportError(
                "anthropic package is required for AnthropicProvider. "
                "Install it with: pip install anthropic"
            ) from e

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.0,
    ) -> str:
        """
        Generate text using Anthropic Claude API.

        Args:
            prompt: The user prompt
            system_prompt: Optional system context
            max_tokens: Maximum response tokens
            temperature: Sampling temperature (0.0-1.0)

        Returns:
            Generated text

        Raises:
            LLMProviderError: If API call fails after retries
            ValueError: If parameters are invalid
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        if max_tokens <= 0:
            raise ValueError("max_tokens must be positive")

        if not 0.0 <= temperature <= 1.0:
            raise ValueError("temperature must be between 0.0 and 1.0")

        # Retry loop for transient failures
        last_error = None
        for attempt in range(self.max_retries):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system_prompt or "",
                    messages=[{"role": "user", "content": prompt}],
                )

                # Track token usage
                self._input_tokens += response.usage.input_tokens
                self._output_tokens += response.usage.output_tokens

                # Extract text from response
                return response.content[0].text

            except Exception as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    delay = self.RETRY_DELAY * (2**attempt)
                    time.sleep(delay)
                continue

        # All retries exhausted
        raise LLMProviderError(
            f"Failed to generate response after {self.max_retries} attempts: {last_error}"
        ) from last_error

    def get_token_usage(self) -> Dict[str, int]:
        """
        Get cumulative token usage.

        Returns:
            Dictionary with 'input_tokens' and 'output_tokens'
        """
        return {
            "input_tokens": self._input_tokens,
            "output_tokens": self._output_tokens,
        }

    def reset_token_usage(self) -> None:
        """Reset token counters."""
        self._input_tokens = 0
        self._output_tokens = 0


# Placeholder for future providers
class OpenAIProvider(LLMProvider):
    """
    OpenAI GPT provider (placeholder for future implementation).

    To add OpenAI support:
    1. Install openai package
    2. Implement generate() using openai.ChatCompletion.create()
    3. Add token tracking from response.usage
    4. Handle API-specific errors and rate limits
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        raise NotImplementedError(
            "OpenAI provider not yet implemented. Use AnthropicProvider for now."
        )

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.0,
    ) -> str:
        raise NotImplementedError

    def get_token_usage(self) -> Dict[str, int]:
        raise NotImplementedError

    def reset_token_usage(self) -> None:
        raise NotImplementedError
