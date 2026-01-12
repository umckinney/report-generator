"""
Report builder for Key Priorities Report.

This module assembles transformed KPR data into the structure needed
for template rendering. This is KPR-specific logic - other reports
will have their own builders with different grouping/sorting needs.
"""

from typing import List, Dict, Any, Tuple
from datetime import datetime
from report_generator.reports.example_report.config import (
    STATUS_CONFIG,
    PRIORITY_STYLES,
    BRAND_COLORS,
    EMPTY_STATES,
    ROLE_DISPLAY_ORDER,
)


class KPRReportBuilder:
    """
    Builds report structure for KPR report.

    Takes flat list of transformed KPR deliverables and organizes them
    for template rendering (grouped by status, sorted by priority, etc.).

    This is KPR-specific. Other reports may group by different fields
    (team, date, etc.) or not group at all.

    Example:
        >>> builder = KPRReportBuilder()
        >>> context = builder.build_context(transformed_data)
        >>> # Pass context to Jinja2 template for rendering
    """

    def _group_by_field(
        self, data: List[Dict[str, Any]], field_name: str
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group data by field value.

        Generic helper method. If this pattern repeats in other reports,
        consider extracting to report_generator.utils.grouping module.

        Args:
            data: List of data dictionaries
            field_name: Name of field to group by

        Returns:
            Dictionary with field values as keys, lists of items as values

        Example:
            >>> groups = builder._group_by_field(data, "status")
            >>> groups["On Track"]
            [{"status": "On Track", ...}, ...]
        """
        groups = {}

        for item in data:
            value = item.get(field_name, "")

            # Handle None or empty values
            if value is None or (isinstance(value, str) and not value.strip()):
                value = ""
            else:
                value = str(value).strip()

            # Initialize group if needed
            if value not in groups:
                groups[value] = []

            groups[value].append(item)

        return groups

    def _sort_by_order_config(
        self, groups: Dict[str, List], order_config: Dict[str, Dict]
    ) -> List[Tuple[str, List]]:
        """
        Sort groups by configured order.

        Generic helper method. If this pattern repeats, consider extracting
        to utils module.

        Args:
            groups: Dictionary of grouped data
            order_config: Configuration with "order" key for each group

        Returns:
            List of (group_name, items) tuples in sorted order

        Example:
            >>> sorted_groups = builder._sort_by_order_config(groups, STATUS_CONFIG)
            >>> # Groups now sorted by STATUS_CONFIG["order"] values
        """

        def get_order(group_name: str) -> int:
            """Get sort order for group. Unknown groups go last."""
            if group_name in order_config:
                return order_config[group_name].get("order", 999)
            return 999  # Unknown groups at the end

        sorted_items = sorted(groups.items(), key=lambda x: get_order(x[0]))

        return sorted_items

    def build_status_groups(
        self, data: List[Dict[str, Any]]
    ) -> List[Tuple[str, List[Dict[str, Any]]]]:
        """
        Build KPR status groups sorted by priority.

        Groups deliverables by status and sorts groups according to
        KPR STATUS_CONFIG order (On Track, At Risk, Off Track, Complete).

        Args:
            data: List of transformed KPR deliverables

        Returns:
            List of (status, deliverables) tuples in sorted order

        Example:
            >>> groups = builder.build_status_groups(data)
            >>> for status, items in groups:
            ...     print(f"{status}: {len(items)} items")
        """
        # Group by status field
        groups = self._group_by_field(data, "status")

        # Sort by KPR status priority
        sorted_groups = self._sort_by_order_config(groups, STATUS_CONFIG)

        return sorted_groups

    def build_context(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Build complete KPR template context.

        Creates the full context dictionary that will be passed to
        the Jinja2 template for rendering the KPR report.

        Args:
            data: List of transformed KPR deliverables

        Returns:
            Dictionary with all data and configuration for KPR template

        Example:
            >>> context = builder.build_context(data)
            >>> # Context includes: status_groups, report_date, KPR config, etc.
        """
        # Build status groups (KPR-specific)
        status_groups = self.build_status_groups(data)

        # Get current date for report
        report_date = datetime.now().strftime("%B %d, %Y")

        # Build KPR-specific context
        context = {
            # Data
            "status_groups": status_groups,
            "total_deliverables": len(data),
            # Metadata
            "report_date": report_date,
            "report_title": "Weekly Key Priorities Report",
            # KPR Configuration
            "brand_colors": BRAND_COLORS,
            "priority_styles": PRIORITY_STYLES,
            "status_config": STATUS_CONFIG,
            "empty_states": EMPTY_STATES,
            "role_display_order": ROLE_DISPLAY_ORDER,
        }

        return context
