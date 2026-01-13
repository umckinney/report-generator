"""
Unit tests for audience-specific renderers.

Tests the renderer abstraction and all three audience implementations:
- ExecutiveRenderer: High-level, decision-focused
- TechnicalRenderer: Complete details
- PartnerRenderer: External-safe, sanitized
"""

from pathlib import Path

import pytest

from report_generator.output.renderers import ExecutiveRenderer, PartnerRenderer, TechnicalRenderer


class TestExecutiveRenderer:
    """Tests for executive audience renderer."""

    @pytest.fixture
    def renderer(self):
        """Create executive renderer with test template directory."""
        template_dir = (
            Path(__file__).parent.parent.parent
            / "src"
            / "report_generator"
            / "reports"
            / "example_report"
        )
        return ExecutiveRenderer(template_dir)

    @pytest.fixture
    def sample_context(self):
        """Sample report context for testing."""
        return {
            "report_title": "Test Report",
            "report_date": "2026-01-12",
            "total_deliverables": 5,
            "status_config": {
                "Off Track": {"color": "#dc3545"},
                "At Risk": {"color": "#ffc107"},
                "On Track": {"color": "#28a745"},
            },
            "status_groups": [
                ("Off Track", [{"deliverable": "API Upgrade", "status": "Off Track"}]),
                ("At Risk", [{"deliverable": "Data Pipeline", "status": "At Risk"}]),
                (
                    "On Track",
                    [
                        {"deliverable": "Feature A", "status": "On Track"},
                        {"deliverable": "Feature B", "status": "On Track"},
                        {"deliverable": "Feature C", "status": "On Track"},
                    ],
                ),
            ],
            "deliverables": [
                {
                    "deliverable": "API Upgrade",
                    "status": "Off Track",
                    "lead": "Alice",
                    "risks_issues": "Understaffed",
                },
                {
                    "deliverable": "Data Pipeline",
                    "status": "At Risk",
                    "lead": "Bob",
                    "risks_issues": "Delayed",
                },
                {
                    "deliverable": "Feature A",
                    "status": "On Track",
                    "lead": "Carol",
                    "risks_issues": "None",
                },
                {
                    "deliverable": "Feature B",
                    "status": "On Track",
                    "lead": "Dave",
                    "risks_issues": "None",
                },
                {
                    "deliverable": "Feature C",
                    "status": "On Track",
                    "lead": "Eve",
                    "risks_issues": "None",
                },
            ],
        }

    def test_get_template_name(self, renderer):
        """Test that executive renderer returns correct template name."""
        assert renderer.get_template_name() == "template_executive.html"

    def test_get_audience_name(self, renderer):
        """Test that executive renderer returns correct audience name."""
        assert renderer.get_audience_name() == "Executive"

    def test_transform_context_filters_critical_items(self, renderer, sample_context):
        """Test that executive renderer filters to show only critical items."""
        transformed = renderer.transform_context(sample_context)

        # Should have filtered status groups
        assert "status_groups_filtered" in transformed

        # Should only include Off Track and At Risk
        filtered_statuses = {status for status, items in transformed["status_groups_filtered"]}
        assert "Off Track" in filtered_statuses
        assert "At Risk" in filtered_statuses
        assert "On Track" not in filtered_statuses

    def test_transform_context_counts_on_track(self, renderer, sample_context):
        """Test that executive renderer counts on-track items."""
        transformed = renderer.transform_context(sample_context)

        # Should count on-track items separately
        assert "on_track_count" in transformed
        assert transformed["on_track_count"] == 3

    def test_transform_context_simplifies_deliverables(self, renderer, sample_context):
        """Test that executive renderer simplifies deliverable details."""
        transformed = renderer.transform_context(sample_context)

        # Should have simplified deliverables
        assert "deliverables_summary" in transformed

        # Check simplified fields
        for summary in transformed["deliverables_summary"]:
            assert "deliverable" in summary
            assert "status" in summary
            assert "lead" in summary
            assert "risks_issues" in summary

    def test_render_includes_audience(self, renderer, sample_context):
        """Test that render output includes audience metadata."""
        html = renderer.render(sample_context, logo_base64="")

        # Should include audience in output (via template)
        assert "Executive" in html or "executive" in html

    def test_transform_preserves_synthesis(self, renderer, sample_context):
        """Test that executive renderer preserves AI synthesis data."""
        sample_context["synthesis"] = {
            "executive_summary": "Program is at risk.",
            "risk_analysis": {"themes": []},
        }

        transformed = renderer.transform_context(sample_context)

        # Synthesis should be preserved
        assert "synthesis" in transformed
        assert transformed["synthesis"]["executive_summary"] == "Program is at risk."
        assert transformed["has_synthesis"] is True
        assert transformed["synthesis_emphasized"] is True


class TestTechnicalRenderer:
    """Tests for technical audience renderer."""

    @pytest.fixture
    def renderer(self):
        """Create technical renderer with test template directory."""
        template_dir = (
            Path(__file__).parent.parent.parent
            / "src"
            / "report_generator"
            / "reports"
            / "example_report"
        )
        return TechnicalRenderer(template_dir)

    @pytest.fixture
    def sample_context(self):
        """Sample report context for testing."""
        return {
            "report_title": "Test Report",
            "total_deliverables": 3,
            "status_groups": [
                ("Off Track", [{"deliverable": "API"}]),
                ("On Track", [{"deliverable": "Feature A"}, {"deliverable": "Feature B"}]),
            ],
            "deliverables": [
                {"deliverable": "API", "status": "Off Track"},
                {"deliverable": "Feature A", "status": "On Track"},
                {"deliverable": "Feature B", "status": "On Track"},
            ],
        }

    def test_get_template_name(self, renderer):
        """Test that technical renderer returns correct template name."""
        assert renderer.get_template_name() == "template_technical.html"

    def test_get_audience_name(self, renderer):
        """Test that technical renderer returns correct audience name."""
        assert renderer.get_audience_name() == "Technical"

    def test_transform_context_shows_all_items(self, renderer, sample_context):
        """Test that technical renderer shows ALL deliverables."""
        transformed = renderer.transform_context(sample_context)

        # Should keep all status groups
        assert "status_groups_filtered" in transformed
        assert len(transformed["status_groups_filtered"]) == 2

        # Should include all deliverables with details
        assert "deliverables_detailed" in transformed
        assert len(transformed["deliverables_detailed"]) == 3

    def test_transform_context_enables_technical_details(self, renderer, sample_context):
        """Test that technical renderer enables technical detail flags."""
        transformed = renderer.transform_context(sample_context)

        # Should enable technical detail flags
        assert transformed["show_technical_details"] is True
        assert transformed["show_all_deliverables"] is True

        # Each deliverable should show all details
        for detail in transformed["deliverables_detailed"]:
            assert detail["show_updates"] is True
            assert detail["show_next_steps"] is True
            assert detail["show_blockers"] is True


class TestPartnerRenderer:
    """Tests for partner audience renderer."""

    @pytest.fixture
    def renderer(self):
        """Create partner renderer with test template directory."""
        template_dir = (
            Path(__file__).parent.parent.parent
            / "src"
            / "report_generator"
            / "reports"
            / "example_report"
        )
        return PartnerRenderer(template_dir)

    @pytest.fixture
    def sample_context(self):
        """Sample report context for testing."""
        return {
            "report_title": "Test Report",
            "total_deliverables": 2,
            "status_groups": [
                ("Off Track", [{"deliverable": "API"}]),
                ("On Track", [{"deliverable": "Feature A"}]),
            ],
            "deliverables": [
                {
                    "deliverable": "API Upgrade",
                    "status": "Off Track",
                    "lead": "Alice Smith",
                    "risks_issues": "Team is understaffed by 2 engineers",
                },
                {
                    "deliverable": "User Features",
                    "status": "On Track",
                    "lead": "Bob Johnson",
                    "risks_issues": "None",
                },
            ],
            "synthesis": {
                "executive_summary": "Project is progressing.",
                "risk_analysis": {
                    "themes": [
                        {
                            "name": "Resource Constraints",
                            "severity": "high",
                            "description": "Staffing issues",
                        },
                        {
                            "name": "Timeline Risk",
                            "severity": "medium",
                            "description": "Minor delays",
                        },
                        {"name": "Documentation", "severity": "low", "description": "Needs update"},
                    ],
                    "critical_risks": [{"deliverable": "API", "reason": "Understaffed"}],
                    "anomalies": [
                        {"deliverable": "Feature X", "issue": "Marked on track but has blockers"}
                    ],
                },
            },
        }

    def test_get_template_name(self, renderer):
        """Test that partner renderer returns correct template name."""
        assert renderer.get_template_name() == "template_partner.html"

    def test_get_audience_name(self, renderer):
        """Test that partner renderer returns correct audience name."""
        assert renderer.get_audience_name() == "Partner"

    def test_transform_context_creates_summary(self, renderer, sample_context):
        """Test that partner renderer creates aggregate status summary."""
        transformed = renderer.transform_context(sample_context)

        # Should create status summary (counts only)
        assert "status_summary" in transformed
        assert transformed["status_summary"]["Off Track"] == 1
        assert transformed["status_summary"]["On Track"] == 1

        # Should not show detailed items
        assert transformed["show_detailed_items"] is False

    def test_transform_context_sanitizes_deliverables(self, renderer, sample_context):
        """Test that partner renderer sanitizes deliverable data."""
        transformed = renderer.transform_context(sample_context)

        # Should have sanitized deliverables
        assert "deliverables_sanitized" in transformed

        # Check sanitization
        for deliverable in transformed["deliverables_sanitized"]:
            # Should hide lead names
            assert deliverable["lead"] == "Internal Team"

            # Should include sanitized risks
            assert "risks_issues" in deliverable

    def test_sanitize_deliverable_hides_leads(self, renderer):
        """Test that partner renderer hides internal lead names."""
        deliverable = {
            "deliverable": "API Upgrade",
            "status": "Off Track",
            "lead": "Alice Smith",
            "risks_issues": "Technical issues",
        }

        sanitized = renderer._sanitize_deliverable(deliverable)

        assert sanitized["lead"] == "Internal Team"
        assert sanitized["deliverable"] == "API Upgrade"
        assert sanitized["status"] == "Off Track"

    def test_sanitize_text_handles_empty(self, renderer):
        """Test that partner renderer handles empty/None risk text."""
        assert renderer._sanitize_text("") == "No issues reported"
        assert renderer._sanitize_text("None") == "No issues reported"
        assert renderer._sanitize_text("N/A") == "No issues reported"

    def test_sanitize_text_truncates_long_descriptions(self, renderer):
        """Test that partner renderer truncates very long internal descriptions."""
        long_text = "x" * 250
        sanitized = renderer._sanitize_text(long_text)

        assert len(sanitized) <= 203  # 200 + "..."
        assert sanitized.endswith("...")

    def test_sanitize_risk_analysis_filters_critical(self, renderer, sample_context):
        """Test that partner renderer filters out critical risks and anomalies."""
        risk_analysis = sample_context["synthesis"]["risk_analysis"]

        sanitized = renderer._sanitize_risk_analysis(risk_analysis)

        # Should only include non-high severity themes
        assert "themes" in sanitized
        theme_severities = {theme["severity"] for theme in sanitized["themes"]}
        assert "high" not in theme_severities
        assert "medium" in theme_severities or "low" in theme_severities

        # Should NOT include critical risks or anomalies
        assert "critical_risks" not in sanitized
        assert "anomalies" not in sanitized

    def test_transform_preserves_sanitized_synthesis(self, renderer, sample_context):
        """Test that partner renderer preserves but sanitizes synthesis."""
        transformed = renderer.transform_context(sample_context)

        # Should have synthesis
        assert "synthesis" in transformed

        # Executive summary should be preserved
        assert transformed["synthesis"]["executive_summary"] == "Project is progressing."

        # Risk analysis should be sanitized
        assert "risk_analysis" in transformed["synthesis"]
        risk_analysis = transformed["synthesis"]["risk_analysis"]

        # Should filter high severity themes
        for theme in risk_analysis.get("themes", []):
            assert theme["severity"] != "high"


class TestRendererIntegration:
    """Integration tests for renderer system."""

    def test_all_renderers_have_unique_templates(self):
        """Test that each renderer uses a different template."""
        template_dir = (
            Path(__file__).parent.parent.parent
            / "src"
            / "report_generator"
            / "reports"
            / "example_report"
        )

        executive = ExecutiveRenderer(template_dir)
        technical = TechnicalRenderer(template_dir)
        partner = PartnerRenderer(template_dir)

        templates = {
            executive.get_template_name(),
            technical.get_template_name(),
            partner.get_template_name(),
        }

        # All three should be different
        assert len(templates) == 3

    def test_all_renderers_have_unique_audiences(self):
        """Test that each renderer has a different audience name."""
        template_dir = (
            Path(__file__).parent.parent.parent
            / "src"
            / "report_generator"
            / "reports"
            / "example_report"
        )

        executive = ExecutiveRenderer(template_dir)
        technical = TechnicalRenderer(template_dir)
        partner = PartnerRenderer(template_dir)

        audiences = {
            executive.get_audience_name(),
            technical.get_audience_name(),
            partner.get_audience_name(),
        }

        # All three should be different
        assert len(audiences) == 3
