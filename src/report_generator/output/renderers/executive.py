"""
Executive renderer for high-level, decision-focused reports.

This renderer targets executive stakeholders who need:
- High-level summary of program health
- Critical items requiring decisions or attention
- Risk themes and trends
- Minimal technical details
"""

from typing import Any, Dict

from report_generator.output.renderers.base import AudienceRenderer


class ExecutiveRenderer(AudienceRenderer):
    """
    Renderer for executive audience.

    Focuses on:
    - Executive summary (AI-generated if available)
    - High-level status counts
    - Only "Off Track" and "At Risk" deliverables (not "On Track")
    - Risk themes and critical issues
    - Action items (if available)

    Omits:
    - Detailed technical descriptions
    - Low-priority "On Track" items
    - Internal process details
    """

    def get_template_name(self) -> str:
        """Return template filename for executive view."""
        return "template_executive.html"

    def get_audience_name(self) -> str:
        """Return human-readable audience name."""
        return "Executive"

    def transform_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform context for executive audience.

        Filters deliverables to show only items requiring attention
        and emphasizes AI-generated insights.

        Args:
            context: Original report context

        Returns:
            Transformed context for executive view
        """
        # Start with copy of original context
        exec_context = {
            **context,
            "view_type": "executive",
            "show_technical_details": False,
        }

        # Filter status groups to prioritize critical items
        # Only show "Off Track" and "At Risk" - executives don't need to see "On Track"
        if "status_groups" in context:
            critical_statuses = {"Off Track", "At Risk"}
            exec_context["status_groups_filtered"] = [
                (status, items)
                for status, items in context["status_groups"]
                if status in critical_statuses
            ]

            # Count on-track items for summary display
            on_track_count = sum(
                len(items)
                for status, items in context["status_groups"]
                if status not in critical_statuses
            )
            exec_context["on_track_count"] = on_track_count

        # Highlight synthesis if available
        if "synthesis" in context and context["synthesis"]:
            exec_context["has_synthesis"] = True
            exec_context["synthesis_emphasized"] = True

        # For deliverables, limit shown details
        if "deliverables" in context:
            # For each deliverable, simplify fields shown
            exec_context["deliverables_summary"] = [
                {
                    "deliverable": d.get("deliverable"),
                    "status": d.get("status"),
                    "lead": d.get("lead"),
                    "risks_issues": d.get("risks_issues"),
                    # Omit detailed fields like "updates", "next_steps", etc.
                }
                for d in context["deliverables"]
            ]

        return exec_context
