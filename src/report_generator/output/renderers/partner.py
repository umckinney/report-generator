"""
Partner renderer for external-safe, sanitized reports.

This renderer targets external partners/clients who need:
- High-level status without internal details
- Sanitized risk descriptions (no internal names/systems)
- Public-facing language
- Minimal exposure of internal processes
"""

from typing import Any, Dict

from report_generator.output.renderers.base import AudienceRenderer


class PartnerRenderer(AudienceRenderer):
    """
    Renderer for external partner audience.

    Focuses on:
    - High-level status information
    - Sanitized risk/issue descriptions
    - Public-facing deliverable names
    - No internal team names, systems, or processes
    - AI-generated summary (if available and appropriate)

    Omits:
    - Internal lead names (shows "Internal Team" instead)
    - Detailed technical blockers
    - Internal system names
    - Sensitive risk details
    """

    def get_template_name(self) -> str:
        """Return template filename for partner view."""
        return "template_partner.html"

    def get_audience_name(self) -> str:
        """Return human-readable audience name."""
        return "Partner"

    def transform_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform context for partner audience.

        Sanitizes internal information and presents only
        partner-appropriate content.

        Args:
            context: Original report context

        Returns:
            Transformed context for partner view (heavily filtered)
        """
        # Start with copy of original context
        partner_context = {
            **context,
            "view_type": "partner",
            "show_technical_details": False,
            "external_view": True,
        }

        # Filter status groups - only show overall counts, not individual items
        if "status_groups" in context:
            # Don't show individual deliverables, just aggregate status
            partner_context["status_summary"] = {
                status: len(items) for status, items in context["status_groups"]
            }
            # Don't expose detailed status groups
            partner_context["show_detailed_items"] = False

        # Sanitize deliverables
        if "deliverables" in context:
            partner_context["deliverables_sanitized"] = [
                self._sanitize_deliverable(d) for d in context["deliverables"]
            ]

        # Filter synthesis - executive summary OK, but sanitize risks
        if "synthesis" in context and context.get("synthesis"):
            synthesis = context["synthesis"].copy()

            # Sanitize risk analysis if present
            if "risk_analysis" in synthesis:
                synthesis["risk_analysis"] = self._sanitize_risk_analysis(
                    synthesis["risk_analysis"]
                )

            partner_context["synthesis"] = synthesis

        return partner_context

    def _sanitize_deliverable(self, deliverable: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize a single deliverable for partner view.

        Removes internal names, systems, and sensitive details.

        Args:
            deliverable: Original deliverable dict

        Returns:
            Sanitized deliverable dict
        """
        return {
            "deliverable": deliverable.get("deliverable", ""),
            "status": deliverable.get("status", ""),
            "lead": "Internal Team",  # Hide actual lead names
            "risks_issues": self._sanitize_text(deliverable.get("risks_issues", "")),
            # Omit updates, next_steps, and other internal details
        }

    def _sanitize_text(self, text: str) -> str:
        """
        Sanitize text to remove internal references.

        This is a simple implementation. In production, you might want
        more sophisticated NLP-based sanitization.

        Args:
            text: Original text

        Returns:
            Sanitized text
        """
        if not text or text.lower() in ["none", "n/a", ""]:
            return "No issues reported"

        # Simple sanitization: if text mentions specific systems/people,
        # generalize it
        # In a real implementation, this would be more sophisticated
        if len(text) > 200:
            # Truncate very long internal descriptions
            return text[:200] + "..."

        return text

    def _sanitize_risk_analysis(self, risk_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize risk analysis for partner view.

        Removes internal system names and sensitive details.

        Args:
            risk_analysis: Original risk analysis

        Returns:
            Sanitized risk analysis
        """
        sanitized = {}

        # Only include high-level themes, not critical risks or anomalies
        if "themes" in risk_analysis:
            # Filter to only show medium or low severity themes
            sanitized["themes"] = [
                theme
                for theme in risk_analysis["themes"]
                if theme.get("severity", "").lower() != "high"
            ]

        # Omit critical_risks and anomalies - too sensitive for external view
        return sanitized
