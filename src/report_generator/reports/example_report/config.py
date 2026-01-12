"""
Configuration for Key Priorities Report.

This module contains all reports-specific configuration including:
- Field mappings from source data to internal names
- Transformations to apply
- Lead role mappings
- Display settings for the template
"""

from report_generator.data.transformers import (
    format_date,
    split_multi_value_names,
    preserve_line_breaks,
)

# ============================================================================
# FIELD MAPPINGS: Airtable Column Name → Internal Field Name
# ============================================================================

FIELD_MAPPINGS = {
    # Core deliverable fields
    "L4 Deliverables": "deliverable",
    "L4 Priority": "priority",
    "Initiatives (L3)": "initiative",
    "Deliverable Status": "status",
    "Event Phase": "event_phase",
    "Delivery Date": "delivery_date",
    # Detail fields
    "Key Achievements": "key_achievements",
    "Risks & Issues": "risks_issues",
}

# ============================================================================
# LEAD ROLE MAPPINGS: Airtable Column Name → Role Display Name
# ============================================================================

LEAD_MAPPINGS = {
    "Product Workstream Lead": "Product",
    "Engineering Workstream Lead": "Engineering",
    "Program Workstream Lead": "Program",
    "Design Workstream Lead": "Design",
    "QA Workstream Lead": "QA",
}

# ============================================================================
# TRANSFORMATIONS: Field Name → Transformation Function
# ============================================================================

# Transformations to apply to specific fields
TRANSFORMATIONS = {
    "delivery_date": format_date,
    "key_achievements": preserve_line_breaks,
    "risks_issues": preserve_line_breaks,
}

# ============================================================================
# DISPLAY CONFIGURATION
# ============================================================================

# Empty state messages (used in template when data is missing)
EMPTY_STATES = {
    "deliverable": "(No deliverable name provided)",
    "delivery_date": "TBD",
    "key_achievements": "No achievements reported this week",
    "risks_issues": "No risks or issues reported this week",
}

# Status display configuration
STATUS_CONFIG = {
    "Off Track": {
        "display": "Off Track",
        "color": "#dc3545",  # Red
        "order": 1,
    },
    "At Risk": {
        "display": "At Risk",
        "color": "#ffc107",  # Yellow
        "order": 2,
    },
    "On Track": {
        "display": "On Track",
        "color": "#28a745",  # Green
        "order": 3,
    },
    "Complete": {
        "display": "Complete",
        "color": "#6c757d",  # Gray
        "order": 4,
    },
}


# Priority display configuration
PRIORITY_STYLES = {
    "P0": {
        "display": "P0",
        "badge_color": "#dc3545",  # Red
        "text_color": "#ffffff",
    },
    "P1": {
        "display": "P1",
        "badge_color": "#fd7e14",  # Orange
        "text_color": "#ffffff",
    },
    "P2": {
        "display": "P2",
        "badge_color": "#ffc107",  # Yellow
        "text_color": "#000000",
    },
    "P3": {
        "display": "P3",
        "badge_color": "#6c757d",  # Gray
        "text_color": "#ffffff",
    },
}

# Brand colors (customize for your organization)
BRAND_COLORS = {
    "primary": "#00338D",  # Primary brand color
    "secondary": "#FFD100",  # Accent color
    "text": "#1a1a1a",
    "background": "#ffffff",
    "border": "#e0e0e0",
}

# Role display order (for consistent layout)
ROLE_DISPLAY_ORDER = [
    "Program",
    "Product",
    "Engineering",
    "Design",
    "QA",
]

# ============================================================================
# EMAIL CONFIGURATION
# ============================================================================

EMAIL_CONFIG = {
    "to": ["your-team@example.com"],  # Configure your recipients
    "cc": [],
    "subject": "Weekly Key Priorities Report - {date}",
    "from_name": "Report Generator",
}

# ============================================================================
# SCHEMA CONFIGURATION (for validation)
# ============================================================================

# Columns expected in the CSV (used by validator for warnings)
EXPECTED_COLUMNS = list(FIELD_MAPPINGS.keys()) + list(LEAD_MAPPINGS.keys())


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def get_transformer_config():
    """
    Get configuration for DataTransformer.

    Returns tuple of (field_mappings, transformations) ready to pass
    to DataTransformer constructor.

    Example:
        >>> field_mappings, transformations = get_transformer_config()
        >>> transformer = DataTransformer(field_mappings, transformations)
    """
    # Combine basic field mappings with lead mappings
    all_field_mappings = FIELD_MAPPINGS.copy()

    # Lead fields will be handled separately, but include in mappings
    for airtable_col, role_name in LEAD_MAPPINGS.items():
        # Map to a temporary field name, we'll restructure in post-processing
        all_field_mappings[airtable_col] = f"_lead_{role_name.lower()}"

    return all_field_mappings, TRANSFORMATIONS


def parse_leads_from_row(transformed_row: dict) -> dict:
    """
    Extract and parse lead information from transformed row.

    Takes a row that's been through DataTransformer and extracts
    the lead fields, splitting multi-value names.

    Args:
        transformed_row: Row that's been through basic transformation

    Returns:
        Dictionary mapping role names to lists of people
        Example: {"Engineering": ["Alice", "Bob"], "Product": ["Carol"]}
    """
    leads = {}

    for role_name in LEAD_MAPPINGS.values():
        field_key = f"_lead_{role_name.lower()}"
        value = transformed_row.get(field_key, "")
        leads[role_name] = split_multi_value_names(value)

    return leads


def clean_transformed_row(row: dict) -> dict:
    """
    Clean up transformed row by removing temporary fields.

    Removes the temporary _lead_* fields and adds structured leads dict.

    Args:
        row: Transformed row with temporary lead fields

    Returns:
        Cleaned row with leads as structured dict
    """
    # Parse leads
    leads = parse_leads_from_row(row)

    # Remove temporary lead fields
    cleaned = {k: v for k, v in row.items() if not k.startswith("_lead_")}

    # Add structured leads
    cleaned["leads"] = leads

    return cleaned
