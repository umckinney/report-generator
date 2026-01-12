"""
LLM reasoning layer for Chief of Staff Agent.

This module provides intelligent synthesis and insight generation capabilities
by integrating with LLM providers (Anthropic Claude, OpenAI, etc.).
"""

from report_generator.reasoning.provider import AnthropicProvider, LLMProvider

__all__ = ["LLMProvider", "AnthropicProvider"]
