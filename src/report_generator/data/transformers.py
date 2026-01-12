"""
Data transformers for reports generator.

This module contains generic utility functions for transforming data.
These functions are reusable across different reports.

Report-specific configuration (field mappings, which transformations to apply)
should live in reports config files, not here.
"""

from datetime import datetime
from typing import Any, Callable, Dict, List, Optional


def split_multi_value_names(value: Optional[str]) -> List[str]:
    """
    Split comma-separated names and remove duplicates.

    This handles fields where multiple people can be assigned to the same role.
    Names are comma-separated in a single cell.

    The function:
    1. Splits on commas
    2. Strips whitespace from each name
    3. Removes duplicates (preserving order of first occurrence)
    4. Filters out empty strings

    Args:
        value: Comma-separated string of names, or None

    Returns:
        List of unique names, preserving order of first occurrence

    Example:
        >>> split_multi_value_names("Alice, Bob, Alice")
        ['Alice', 'Bob']

        >>> split_multi_value_names("")
        []

        >>> split_multi_value_names(None)
        []
    """
    if not value:
        return []

    # Split on comma
    names = value.split(",")

    # Strip whitespace and filter empty strings
    names = [name.strip() for name in names]
    names = [name for name in names if name]

    # Remove duplicates while preserving order
    # Using dict.fromkeys() preserves insertion order (Python 3.7+)
    unique_names = list(dict.fromkeys(names))

    return unique_names


def format_date(date_value: Optional[str]) -> str:
    """
    Format date string from MM/DD/YYYY to Mon DD, YYYY.

    Returns empty string for missing or invalid dates.
    Template/presentation layer decides how to display empty values.

    Args:
        date_value: Date string in MM/DD/YYYY format, or None

    Returns:
        Formatted date string (e.g., "Dec 15, 2024") or empty string

    Example:
        >>> format_date("12/15/2024")
        'Dec 15, 2024'

        >>> format_date("")
        ''

        >>> format_date(None)
        ''

        >>> format_date("invalid")
        ''
    """
    if not date_value:
        return ""

    # Try to parse the date
    try:
        # Handle MM/DD/YYYY format
        date_obj = datetime.strptime(str(date_value).strip(), "%m/%d/%Y")

        # Format as "Mon DD, YYYY"
        return date_obj.strftime("%b %d, %Y")

    except (ValueError, AttributeError):
        # If date is invalid or in unexpected format, return empty string
        # Template will decide how to display (e.g., "TBD", "N/A", etc.)
        return ""


class DataTransformer:
    """
    Generic data transformer driven by configuration.

    This class maps source columns to target field names and applies
    transformation functions as specified. It is NOT tied to any specific
    reports - all reports-specific logic comes from configuration.

    Example:
        >>> field_mappings = {
        ...     "Source Column": "target_field",
        ...     "Date Column": "formatted_date"
        ... }
        >>> transformations = {
        ...     "formatted_date": format_date
        ... }
        >>> transformer = DataTransformer(field_mappings, transformations)
        >>> result = transformer.transform_row({"Source Column": "value"})
    """

    def __init__(
        self,
        field_mappings: Dict[str, str],
        transformations: Dict[str, Callable] = None,
    ):
        """
        Initialize transformer with reports-specific configuration.

        Args:
            field_mappings: Dictionary mapping source column names to target field names.
                Example: {"L4 Deliverables": "deliverable"}

            transformations: Optional dictionary mapping target field names to
                transformation functions. Functions should accept a single value
                and return the transformed value.
                Example: {"delivery_date": format_date}
        """
        self.field_mappings = field_mappings
        self.transformations = transformations or {}

    def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform all rows of data.

        Applies field mappings and transformations to each row.

        Args:
            data: List of raw data dictionaries

        Returns:
            List of transformed data dictionaries

        Example:
            >>> raw_data = [{"Name": "Alice"}, {"Name": "Bob"}]
            >>> transformer = DataTransformer({"Name": "name"})
            >>> result = transformer.transform(raw_data)
            >>> result[0]["name"]
            'Alice'
        """
        return [self.transform_row(row) for row in data]

    def transform_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform a single row of data.

        Maps source columns to target fields and applies any configured
        transformation functions.

        Args:
            row: Raw data dictionary

        Returns:
            Transformed data dictionary with target field names

        Example:
            >>> field_mappings = {"Old Name": "new_name"}
            >>> transformer = DataTransformer(field_mappings)
            >>> result = transformer.transform_row({"Old Name": "value"})
            >>> result["new_name"]
            'value'
        """
        transformed = {}

        for source_col, target_field in self.field_mappings.items():
            # Get value from source column (empty string if missing)
            value = row.get(source_col, "")

            # Apply transformation if configured for this field
            if target_field in self.transformations:
                transformation_func = self.transformations[target_field]
                value = transformation_func(value)
            else:
                # Default behavior: strip whitespace, handle None
                if value is None:
                    value = ""
                else:
                    value = str(value).strip()

            transformed[target_field] = value

        return transformed


def preserve_line_breaks(value: Optional[str]) -> str:
    """
    Convert newlines to HTML <br> tags for display.

    This preserves line breaks when displaying multi-line text fields
    in HTML templates (like Key Achievements and Risks & Issues).
    Handles both Unix (\\n) and Windows (\\r\\n) line endings.

    Args:
        value: Text that may contain newlines, or None

    Returns:
        Text with newlines converted to <br> tags, or empty string

    Example:
        >>> preserve_line_breaks("Line 1\\nLine 2\\nLine 3")
        'Line 1<br>Line 2<br>Line 3'

        >>> preserve_line_breaks("Line 1\\r\\nLine 2")
        'Line 1<br>Line 2'

        >>> preserve_line_breaks("")
        ''

        >>> preserve_line_breaks(None)
        ''
    """
    if not value:
        return ""

    # Strip leading/trailing whitespace first
    text = str(value).strip()

    # Handle Windows line endings first (\r\n)
    text = text.replace("\r\n", "<br>")

    # Then handle Unix line endings (\n)
    text = text.replace("\n", "<br>")

    # Handle any remaining \r (old Mac style, rare)
    text = text.replace("\r", "<br>")

    return text
