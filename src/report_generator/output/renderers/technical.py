"""
Technical renderer for detailed, engineering-focused reports.

This renderer targets technical stakeholders who need:
- Complete deliverable details
- Technical blockers and dependencies
- Detailed status updates and next steps
- Full context for debugging and planning
"""

from typing import Any, Dict

from report_generator.output.renderers.base import AudienceRenderer


class TechnicalRenderer(AudienceRenderer):
    """
    Renderer for technical audience.

    Focuses on:
    - All deliverables with complete details
    - Technical updates and next steps
    - Blockers and dependencies
    - Resource allocation details
    - Full risk descriptions

    This is the most comprehensive view, similar to the default
    template but optimized for technical stakeholders.
    """

    def get_template_name(self) -> str:
        """Return template filename for technical view."""
        return "template_technical.html"

    def get_audience_name(self) -> str:
        """Return human-readable audience name."""
        return "Technical"

    def transform_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform context for technical audience.

        Technical view shows ALL information - no filtering.
        May add technical-specific enhancements in the future.

        Args:
            context: Original report context

        Returns:
            Transformed context for technical view (minimal changes)
        """
        # Start with copy of original context
        tech_context = {
            **context,
            "view_type": "technical",
            "show_technical_details": True,
            "show_all_deliverables": True,
        }

        # Technical view: group deliverables by status but show ALL
        if "status_groups" in context:
            # Keep all status groups
            tech_context["status_groups_filtered"] = context["status_groups"]

        # Emphasize technical fields
        if "deliverables" in context:
            # Add technical metadata if available
            tech_context["deliverables_detailed"] = [
                {
                    **d,  # Include ALL fields
                    "show_updates": True,
                    "show_next_steps": True,
                    "show_blockers": True,
                }
                for d in context["deliverables"]
            ]

        # Highlight risk analysis for technical debugging
        if "synthesis" in context and context.get("synthesis", {}).get("risk_analysis"):
            tech_context["risk_analysis_expanded"] = True

        return tech_context
