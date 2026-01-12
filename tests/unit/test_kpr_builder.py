"""
Unit tests for KPR report builder.

Tests the logic that assembles transformed KPR data into a structure
ready for template rendering (grouping by status, sorting, etc.).

This is KPR-specific logic. Other reports will have their own builders.
"""

import pytest
from report_generator.reports.example_report.builder import KPRReportBuilder


class TestKPRReportBuilder:
    """Tests for KPR-specific report builder."""

    def test_group_by_status(self):
        """
        Test grouping KPR deliverables by status.

        Should create dict with status as keys, deliverables as values.
        """
        data = [
            {"deliverable": "Item 1", "status": "On Track"},
            {"deliverable": "Item 2", "status": "At Risk"},
            {"deliverable": "Item 3", "status": "On Track"},
        ]

        builder = KPRReportBuilder()
        grouped = builder._group_by_field(data, "status")

        assert "On Track" in grouped
        assert "At Risk" in grouped
        assert len(grouped["On Track"]) == 2
        assert len(grouped["At Risk"]) == 1

    def test_group_by_status_with_empty_status(self):
        """
        Test grouping when some items have empty status.

        Should group empty/None status items under "(Unknown)".
        """
        data = [
            {"deliverable": "Item 1", "status": "On Track"},
            {"deliverable": "Item 2", "status": ""},
            {"deliverable": "Item 3", "status": None},
        ]

        builder = KPRReportBuilder()
        grouped = builder._group_by_field(data, "status")

        assert "On Track" in grouped
        # Empty/None statuses should be grouped as ""
        assert "" in grouped
        assert len(grouped[""]) == 2

    def test_sort_groups_by_status_order(self):
        """
        Test that status groups are sorted by KPR status order.

        Order should be: On Track, At Risk, Off Track, Complete
        """
        data = [
            {"deliverable": "Item 1", "status": "Complete"},
            {"deliverable": "Item 2", "status": "On Track"},
            {"deliverable": "Item 3", "status": "Off Track"},
            {"deliverable": "Item 4", "status": "At Risk"},
        ]

        builder = KPRReportBuilder()
        sorted_groups = builder.build_status_groups(data)

        # Should be list of (status, items) tuples in order
        assert len(sorted_groups) == 4

        # Check order
        statuses = [status for status, items in sorted_groups]
        assert statuses.index("Off Track") < statuses.index("At Risk")
        assert statuses.index("At Risk") < statuses.index("On Track")
        assert statuses.index("On Track") < statuses.index("Complete")

    def test_build_report_context(self):
        """
        Test building complete KPR report context for template.

        Should include data, metadata, configuration.
        """
        data = [
            {"deliverable": "Item 1", "status": "On Track", "priority": "P0"},
        ]

        builder = KPRReportBuilder()
        context = builder.build_context(data)

        # Should have status groups
        assert "status_groups" in context

        # Should have metadata
        assert "report_date" in context
        assert "report_title" in context

        # Should have KPR config
        assert "brand_colors" in context
        assert "priority_styles" in context
        assert "status_config" in context
