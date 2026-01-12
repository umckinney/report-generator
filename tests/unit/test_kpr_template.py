"""
Unit tests for KPR template rendering.

Tests that the Jinja2 template for Key Priorities report
renders correctly with context data.

This is KPR-specific. Other reports will have their own template tests.
"""

from pathlib import Path

import pytest
from jinja2 import Environment, FileSystemLoader

from report_generator.reports.example_report.builder import KPRReportBuilder


class TestTemplateRendering:
    """Tests for KPR template rendering."""

    def test_template_renders_without_error(self):
        """
        Test that template renders with minimal context.

        Should not raise any Jinja2 errors.
        """
        # Setup Jinja2 environment
        template_dir = Path("src/report_generator/reports/example_report")
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template("template.html")

        # Minimal context
        builder = KPRReportBuilder()
        context = builder.build_context([])

        # Should render without error
        html = template.render(context)

        assert html is not None
        assert len(html) > 0
        assert "<!DOCTYPE html>" in html

    def test_template_renders_with_data(self):
        """
        Test that template renders with actual data.

        Should include deliverable names, status, etc.
        """
        # Setup template
        template_dir = Path("src/report_generator/reports/example_report")
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template("template.html")

        # Sample data
        data = [
            {
                "deliverable": "Test Deliverable 1",
                "status": "On Track",
                "priority": "P0",
                "initiative": "Test Initiative",
                "event_phase": "In Development",
                "delivery_date": "Dec 15, 2024",
                "key_achievements": "Made progress",
                "risks_issues": "No issues",
                "leads": {
                    "Engineering": ["Alice", "Bob"],
                    "Product": ["Carol"],
                    "Program": [],
                    "Design": [],
                    "QA": [],
                },
            }
        ]

        # Build context and render
        builder = KPRReportBuilder()
        context = builder.build_context(data)
        html = template.render(context)

        # Verify content is present
        assert "Test Deliverable 1" in html
        assert "On Track" in html
        assert "P0" in html
        assert "Alice" in html
        assert "Carol" in html

    def test_template_handles_empty_values(self):
        """
        Test that template handles empty/missing values gracefully.

        Should display empty state messages from config.
        """
        # Setup template
        template_dir = Path("src/report_generator/reports/example_report")
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template("template.html")

        # Data with empty values
        data = [
            {
                "deliverable": "",
                "status": "",
                "priority": "",
                "initiative": "",
                "event_phase": "",
                "delivery_date": "",
                "key_achievements": "",
                "risks_issues": "",
                "leads": {
                    "Engineering": [],
                    "Product": [],
                    "Program": [],
                    "Design": [],
                    "QA": [],
                },
            }
        ]

        # Build context and render
        builder = KPRReportBuilder()
        context = builder.build_context(data)
        html = template.render(context)

        # Should render without error
        assert html is not None
        assert len(html) > 0
