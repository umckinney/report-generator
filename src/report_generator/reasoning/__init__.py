"""
LLM reasoning layer for Chief of Staff Agent.

This module provides intelligent synthesis and insight generation capabilities
by integrating with LLM providers (Anthropic Claude, OpenAI, etc.).
"""

from report_generator.reasoning.config import ReasoningConfig, get_config
from report_generator.reasoning.provider import AnthropicProvider, LLMProvider
from report_generator.reasoning.synthesizer import ReportSynthesizer

__all__ = [
    "LLMProvider",
    "AnthropicProvider",
    "ReportSynthesizer",
    "ReasoningConfig",
    "get_config",
]
