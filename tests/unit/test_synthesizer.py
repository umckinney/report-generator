"""
Unit tests for ReportSynthesizer.
"""

from unittest.mock import Mock

import pytest

from report_generator.reasoning.synthesizer import ReportSynthesizer


class TestReportSynthesizer:
    """Tests for ReportSynthesizer."""

    def test_init(self):
        """Test synthesizer initialization."""
        mock_provider = Mock()
        synthesizer = ReportSynthesizer(mock_provider, max_tokens=1000, temperature=0.5)

        assert synthesizer.provider is mock_provider
        assert synthesizer.max_tokens == 1000
        assert synthesizer.temperature == 0.5

    def test_synthesize_with_executive_summary(self):
        """Test synthesis with executive summary enabled."""
        mock_provider = Mock()
        mock_provider.generate.return_value = "Program is on track with 2 at-risk items requiring attention."
        mock_provider.model = "claude-sonnet-4-5"

        synthesizer = ReportSynthesizer(mock_provider)

        context = {
            "total_deliverables": 10,
            "status_groups": [
                ("On Track", [{"deliverable": "Feature A"}]),
                ("At Risk", [{"deliverable": "Feature B"}]),
            ],
            "report_date": "January 12, 2026",
        }

        result = synthesizer.synthesize(context, features={"executive_summary": True})

        # Original context preserved
        assert result["total_deliverables"] == 10
        assert result["status_groups"] == context["status_groups"]

        # Synthesis added
        assert "synthesis" in result
        assert result["synthesis"]["executive_summary"] == "Program is on track with 2 at-risk items requiring attention."
        assert "generated_at" in result["synthesis"]
        assert result["synthesis"]["model"] == "claude-sonnet-4-5"

    def test_synthesize_default_features(self):
        """Test that default features include executive summary and risk analysis."""
        mock_provider = Mock()
        # First call for executive summary, second for risk analysis
        mock_provider.generate.side_effect = [
            "Summary text",
            '{"themes": [], "critical_risks": [], "anomalies": []}',
        ]
        mock_provider.model = "claude-sonnet-4-5"

        synthesizer = ReportSynthesizer(mock_provider)
        context = {
            "total_deliverables": 5,
            "status_groups": [
                ("At Risk", [{"deliverable": "A", "risks_issues": "Real risk"}])
            ],
        }

        result = synthesizer.synthesize(context)  # No features specified

        assert "synthesis" in result
        assert "executive_summary" in result["synthesis"]
        assert "risk_analysis" in result["synthesis"]

    def test_synthesize_executive_summary_disabled(self):
        """Test synthesis with executive summary disabled."""
        mock_provider = Mock()
        synthesizer = ReportSynthesizer(mock_provider)

        context = {"total_deliverables": 5, "status_groups": []}

        result = synthesizer.synthesize(
            context, features={"executive_summary": False}
        )

        assert "synthesis" in result
        assert "executive_summary" not in result["synthesis"]
        # Provider should not have been called
        mock_provider.generate.assert_not_called()

    def test_synthesize_graceful_degradation(self):
        """Test that synthesis fails gracefully on LLM error."""
        mock_provider = Mock()
        mock_provider.generate.side_effect = Exception("API error")
        mock_provider.model = "claude-sonnet-4-5"

        synthesizer = ReportSynthesizer(mock_provider)
        context = {"total_deliverables": 5, "status_groups": []}

        # Should not raise exception
        result = synthesizer.synthesize(context, features={"executive_summary": True})

        assert "synthesis" in result
        assert result["synthesis"]["executive_summary"] is None
        assert "executive_summary_error" in result["synthesis"]
        assert "API error" in result["synthesis"]["executive_summary_error"]

    def test_synthesize_preserves_original_context(self):
        """Test that synthesis doesn't modify original context."""
        mock_provider = Mock()
        mock_provider.generate.return_value = "Summary"
        mock_provider.model = "test"

        synthesizer = ReportSynthesizer(mock_provider)

        original_context = {
            "total_deliverables": 10,
            "status_groups": [("On Track", [])],
        }

        result = synthesizer.synthesize(original_context)

        # Original context should be unchanged
        assert "synthesis" not in original_context
        # Result should have synthesis
        assert "synthesis" in result
        # Original fields preserved
        assert result["total_deliverables"] == 10

    def test_get_token_usage(self):
        """Test token usage retrieval."""
        mock_provider = Mock()
        mock_provider.get_token_usage.return_value = {
            "input_tokens": 200,
            "output_tokens": 50,
        }

        synthesizer = ReportSynthesizer(mock_provider)
        usage = synthesizer.get_token_usage()

        assert usage["input_tokens"] == 200
        assert usage["output_tokens"] == 50
        mock_provider.get_token_usage.assert_called_once()

    def test_reset_token_usage(self):
        """Test token usage reset."""
        mock_provider = Mock()
        synthesizer = ReportSynthesizer(mock_provider)

        synthesizer.reset_token_usage()
        mock_provider.reset_token_usage.assert_called_once()

    def test_executive_summary_calls_provider_correctly(self):
        """Test that executive summary generation calls provider with correct params."""
        mock_provider = Mock()
        mock_provider.generate.return_value = "Test summary"
        mock_provider.model = "test"

        synthesizer = ReportSynthesizer(
            mock_provider, max_tokens=1000, temperature=0.3
        )

        context = {
            "total_deliverables": 5,
            "status_groups": [],
            "report_date": "Test Date",
        }

        synthesizer.synthesize(
            context, features={"executive_summary": True, "risk_analysis": False}
        )

        # Verify provider was called with correct parameters
        mock_provider.generate.assert_called_once()
        call_args = mock_provider.generate.call_args

        assert call_args.kwargs["max_tokens"] == 1000
        assert call_args.kwargs["temperature"] == 0.3
        assert "system_prompt" in call_args.kwargs
        assert "technical program manager" in call_args.kwargs["system_prompt"]
        assert "prompt" in call_args.kwargs
        # Prompt should contain context data
        assert "Test Date" in call_args.kwargs["prompt"]

    def test_synthesize_with_risk_analysis(self):
        """Test synthesis with risk analysis enabled."""
        mock_provider = Mock()
        mock_provider.generate.return_value = """{
            "themes": [
                {
                    "name": "Resource Constraints",
                    "description": "Multiple teams facing staffing issues",
                    "affected_deliverables": ["Feature A", "Feature B"],
                    "severity": "high"
                }
            ],
            "critical_risks": [
                {
                    "deliverable": "Feature A",
                    "risk": "Team understaffed",
                    "reason": "Impacts launch timeline"
                }
            ],
            "anomalies": []
        }"""
        mock_provider.model = "claude-sonnet-4-5"

        synthesizer = ReportSynthesizer(mock_provider)

        context = {
            "status_groups": [
                (
                    "At Risk",
                    [
                        {
                            "deliverable": "Feature A",
                            "risks_issues": "Resource constraints",
                        }
                    ],
                )
            ]
        }

        result = synthesizer.synthesize(
            context, features={"executive_summary": False, "risk_analysis": True}
        )

        # Risk analysis added
        assert "synthesis" in result
        assert "risk_analysis" in result["synthesis"]
        assert len(result["synthesis"]["risk_analysis"]["themes"]) == 1
        assert (
            result["synthesis"]["risk_analysis"]["themes"][0]["name"]
            == "Resource Constraints"
        )
        assert len(result["synthesis"]["risk_analysis"]["critical_risks"]) == 1

    def test_synthesize_risk_analysis_no_risks(self):
        """Test risk analysis when no risks to analyze."""
        mock_provider = Mock()
        synthesizer = ReportSynthesizer(mock_provider)

        context = {
            "status_groups": [
                (
                    "On Track",
                    [
                        {
                            "deliverable": "Feature A",
                            "risks_issues": "No risks or issues reported this week",
                        }
                    ],
                )
            ]
        }

        result = synthesizer.synthesize(
            context, features={"executive_summary": False, "risk_analysis": True}
        )

        # Risk analysis should not be present
        assert "synthesis" in result
        assert "risk_analysis" not in result["synthesis"]
        # Provider should not have been called
        mock_provider.generate.assert_not_called()

    def test_synthesize_risk_analysis_graceful_degradation(self):
        """Test that risk analysis fails gracefully on LLM error."""
        mock_provider = Mock()
        mock_provider.generate.side_effect = Exception("API error")
        mock_provider.model = "claude-sonnet-4-5"

        synthesizer = ReportSynthesizer(mock_provider)
        context = {
            "status_groups": [
                ("At Risk", [{"deliverable": "A", "risks_issues": "Real risk"}])
            ]
        }

        # Should not raise exception
        result = synthesizer.synthesize(
            context, features={"executive_summary": False, "risk_analysis": True}
        )

        assert "synthesis" in result
        assert result["synthesis"]["risk_analysis"] is None
        assert "risk_analysis_error" in result["synthesis"]
        assert "API error" in result["synthesis"]["risk_analysis_error"]

    def test_risk_analysis_calls_provider_correctly(self):
        """Test that risk analysis calls provider with correct params."""
        mock_provider = Mock()
        mock_provider.generate.return_value = (
            '{"themes": [], "critical_risks": [], "anomalies": []}'
        )
        mock_provider.model = "test"

        synthesizer = ReportSynthesizer(
            mock_provider, max_tokens=1000, temperature=0.3
        )

        context = {
            "status_groups": [
                ("At Risk", [{"deliverable": "A", "risks_issues": "Real risk"}])
            ]
        }

        synthesizer.synthesize(
            context, features={"executive_summary": False, "risk_analysis": True}
        )

        # Verify provider was called with correct parameters
        mock_provider.generate.assert_called_once()
        call_args = mock_provider.generate.call_args

        assert call_args.kwargs["max_tokens"] == 1000
        assert call_args.kwargs["temperature"] == 0.3
        assert "system_prompt" in call_args.kwargs
        assert "analyzing program risks" in call_args.kwargs["system_prompt"]
        assert "JSON" in call_args.kwargs["system_prompt"]
        assert "prompt" in call_args.kwargs
        # Prompt should contain risk data
        assert "Real risk" in call_args.kwargs["prompt"]
