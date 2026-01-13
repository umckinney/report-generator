"""
Report synthesizer for LLM-powered analysis.

This module orchestrates LLM reasoning over structured report data,
generating executive summaries, risk analysis, and other insights.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from report_generator.reasoning.prompts import executive_summary, risk_analysis
from report_generator.reasoning.provider import LLMProvider


class ReportSynthesizer:
    """
    Orchestrates LLM reasoning over structured report data.

    The synthesizer takes cleaned, structured report context and generates
    AI-powered insights like executive summaries, risk analysis, and themes.

    Example:
        >>> from report_generator.reasoning import AnthropicProvider
        >>> provider = AnthropicProvider()
        >>> synthesizer = ReportSynthesizer(provider)
        >>> context = {"status_groups": [...], "total_deliverables": 10}
        >>> enriched = synthesizer.synthesize(context)
        >>> print(enriched["synthesis"]["executive_summary"])
    """

    def __init__(
        self,
        provider: LLMProvider,
        max_tokens: int = 500,
        temperature: float = 0.0,
    ):
        """
        Initialize synthesizer with LLM provider.

        Args:
            provider: LLM provider instance (e.g., AnthropicProvider)
            max_tokens: Default max tokens for generation
            temperature: Default temperature (0.0 = deterministic)
        """
        self.provider = provider
        self.max_tokens = max_tokens
        self.temperature = temperature

    def synthesize(
        self,
        context: Dict[str, Any],
        features: Optional[Dict[str, bool]] = None,
    ) -> Dict[str, Any]:
        """
        Generate insights from report context.

        Takes structured report data and returns an enriched version with
        AI-generated synthesis (executive summary, risks, themes, etc.).

        The original context is preserved unchanged - synthesis is added
        under a "synthesis" key.

        Args:
            context: Structured data from builder (status_groups, deliverables, etc.)
            features: Optional dict to enable/disable features
                     {"executive_summary": True, "risk_analysis": False, ...}

        Returns:
            Enhanced context with synthesis results

        Example:
            >>> context = {"total_deliverables": 5, "status_groups": [...]}
            >>> result = synthesizer.synthesize(context)
            >>> result["synthesis"]["executive_summary"]
            'Program is on track with 1 at-risk deliverable...'
        """
        # Default features
        if features is None:
            features = {
                "executive_summary": True,
                "risk_analysis": True,  # Phase 3 - Now available!
                "action_items": False,  # Phase 5
            }

        synthesis = {
            "generated_at": datetime.now().isoformat(),
            "model": getattr(self.provider, "model", "unknown"),
        }

        # Generate executive summary
        if features.get("executive_summary", False):
            try:
                summary_result = self._generate_executive_summary(context)
                synthesis["executive_summary"] = summary_result["summary"]
                synthesis["executive_summary_metadata"] = {
                    "length": summary_result["length"],
                    "sentence_count": summary_result["sentence_count"],
                }
            except Exception as e:
                # Graceful degradation: log error but don't crash
                synthesis["executive_summary"] = None
                synthesis["executive_summary_error"] = str(e)

        # Risk analysis
        if features.get("risk_analysis", False):
            try:
                risk_result = self._analyze_risks(context)
                if risk_result:  # Only add if there are risks to analyze
                    synthesis["risk_analysis"] = risk_result
            except Exception as e:
                synthesis["risk_analysis"] = None
                synthesis["risk_analysis_error"] = str(e)

        # Return original context + synthesis
        return {
            **context,  # Original data preserved
            "synthesis": synthesis,
        }

    def _generate_executive_summary(
        self, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate 2-3 sentence executive summary.

        Args:
            context: Report context

        Returns:
            Dictionary with summary text and metadata
        """
        # Build prompt
        prompt = executive_summary.build_prompt(context)

        # Call LLM
        response = self.provider.generate(
            prompt=prompt,
            system_prompt=(
                "You are an AI assistant helping a technical program manager "
                "understand program status. Be concise, specific, and decision-oriented."
            ),
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )

        # Parse response
        parsed = executive_summary.parse_response(response)

        return parsed

    def _analyze_risks(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Analyze risks and extract themes.

        Args:
            context: Report context

        Returns:
            Dictionary with themes, critical risks, and anomalies, or None if no risks
        """
        # Build prompt
        prompt = risk_analysis.build_prompt(context)

        if prompt is None:
            # No risks to analyze
            return None

        # Call LLM
        response = self.provider.generate(
            prompt=prompt,
            system_prompt=(
                "You are an AI assistant analyzing program risks. "
                "Return valid JSON only. Be concise and specific."
            ),
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )

        # Parse response
        parsed = risk_analysis.parse_response(response)

        return parsed

    def get_token_usage(self) -> Dict[str, int]:
        """
        Get cumulative token usage from provider.

        Returns:
            Dictionary with 'input_tokens' and 'output_tokens'
        """
        return self.provider.get_token_usage()

    def reset_token_usage(self) -> None:
        """Reset token usage counters."""
        self.provider.reset_token_usage()
