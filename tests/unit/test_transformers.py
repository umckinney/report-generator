"""
Unit tests for data transformers.

Tests generic transformation utilities that can be used across
different reports. Report-specific logic lives in reports config.
"""

import pytest
from report_generator.data.transformers import (
    format_date,
    split_multi_value_names,
    DataTransformer,
    preserve_line_breaks,
)


class TestSplitMultiValueNames:
    """Tests for multi-value name splitting function."""

    def test_split_comma_separated_names(self):
        """
        Test splitting comma-separated names.

        Should split on commas and strip whitespace.
        """
        result = split_multi_value_names("Alice Smith, Bob Jones, Carol White")

        assert result == ["Alice Smith", "Bob Jones", "Carol White"]

    def test_split_and_deduplicate(self):
        """
        Test splitting and removing duplicates.

        Should preserve order of first occurrence.
        """
        result = split_multi_value_names("Alice, Bob, Alice, Carol")

        assert "Alice" in result
        assert "Bob" in result
        assert "Carol" in result
        assert len(result) == 3  # No duplicates
        assert result[0] == "Alice"  # First occurrence preserved

    def test_split_single_name(self):
        """
        Test handling of single name (no commas).

        Should return list with one name.
        """
        result = split_multi_value_names("Alice Smith")

        assert result == ["Alice Smith"]

    def test_split_empty_string(self):
        """
        Test handling of empty string.

        Should return empty list.
        """
        result = split_multi_value_names("")

        assert result == []

    def test_split_none_value(self):
        """
        Test handling of None value.

        Should return empty list.
        """
        result = split_multi_value_names(None)

        assert result == []

    def test_split_with_extra_whitespace(self):
        """
        Test handling of extra whitespace around names.

        Should strip whitespace from each name.
        """
        result = split_multi_value_names("  Alice  ,  Bob  ,  Carol  ")

        assert result == ["Alice", "Bob", "Carol"]

    def test_split_with_empty_values(self):
        """
        Test handling of empty values in list.

        Input: "Alice, , Bob, ,"
        Should filter out empty strings.
        """
        result = split_multi_value_names("Alice, , Bob, ,")

        assert result == ["Alice", "Bob"]


class TestFormatDate:
    """Tests for date formatting function."""

    def test_format_valid_date(self):
        """
        Test formatting a valid date.

        Input: "12/15/2024"
        Output: "Dec 15, 2024"
        """
        result = format_date("12/15/2024")

        assert result == "Dec 15, 2024"

    def test_format_empty_string(self):
        """
        Test formatting empty string.

        Should return empty string (template decides display).
        """
        result = format_date("")

        assert result == ""

    def test_format_none_value(self):
        """
        Test formatting None value.

        Should return empty string (template decides display).
        """
        result = format_date(None)

        assert result == ""

    def test_format_different_date_formats(self):
        """
        Test handling different input date formats.

        Should handle common formats gracefully.
        """
        # MM/DD/YYYY format
        result1 = format_date("1/5/2024")
        assert result1 == "Jan 05, 2024"

        # M/D/YYYY format (single digits)
        result2 = format_date("12/5/2024")
        assert result2 == "Dec 05, 2024"

    def test_format_invalid_date(self):
        """
        Test handling invalid date string.

        Should return empty string (graceful degradation).
        Template decides how to display.
        """
        result = format_date("not a date")

        assert result == ""

    def test_format_with_leading_trailing_whitespace(self):
        """
        Test that whitespace is handled correctly.

        Should strip whitespace before parsing.
        """
        result = format_date("  12/15/2024  ")

        assert result == "Dec 15, 2024"


class TestDataTransformer:
    """Tests for generic DataTransformer class."""

    def test_transform_with_simple_mappings(self):
        """
        Test transformer with simple field mappings (no transformations).

        Should map source columns to target field names.
        """
        field_mappings = {
            "Source Column A": "target_a",
            "Source Column B": "target_b",
        }

        raw_row = {
            "Source Column A": "Value A",
            "Source Column B": "Value B",
        }

        transformer = DataTransformer(field_mappings)
        result = transformer.transform_row(raw_row)

        assert result["target_a"] == "Value A"
        assert result["target_b"] == "Value B"

    def test_transform_with_transformation_functions(self):
        """
        Test transformer with transformation functions.

        Should apply specified transformations to fields.
        """
        field_mappings = {
            "Date Column": "formatted_date",
            "Names Column": "name_list",
        }

        transformations = {
            "formatted_date": format_date,
            "name_list": split_multi_value_names,
        }

        raw_row = {
            "Date Column": "12/15/2024",
            "Names Column": "Alice, Bob, Alice",
        }

        transformer = DataTransformer(field_mappings, transformations)
        result = transformer.transform_row(raw_row)

        assert result["formatted_date"] == "Dec 15, 2024"
        assert result["name_list"] == ["Alice", "Bob"]

    def test_transform_with_missing_source_columns(self):
        """
        Test transformer when source columns are missing.

        Should handle missing columns gracefully with empty strings.
        """
        field_mappings = {
            "Column A": "field_a",
            "Column B": "field_b",
        }

        raw_row = {
            "Column A": "Value A",
            # Column B missing
        }

        transformer = DataTransformer(field_mappings)
        result = transformer.transform_row(raw_row)

        assert result["field_a"] == "Value A"
        assert result["field_b"] == ""  # Missing column = empty string

    def test_transform_strips_whitespace_by_default(self):
        """
        Test that transformer strips whitespace by default.

        Unless a transformation function is specified, values should
        be stripped of leading/trailing whitespace.
        """
        field_mappings = {
            "Column": "field",
        }

        raw_row = {
            "Column": "  Value with spaces  ",
        }

        transformer = DataTransformer(field_mappings)
        result = transformer.transform_row(raw_row)

        assert result["field"] == "Value with spaces"

    def test_transform_handles_none_values(self):
        """
        Test transformer with None values.

        Should convert None to empty string.
        """
        field_mappings = {
            "Column": "field",
        }

        raw_row = {
            "Column": None,
        }

        transformer = DataTransformer(field_mappings)
        result = transformer.transform_row(raw_row)

        assert result["field"] == ""

    def test_transform_multiple_rows(self):
        """
        Test transforming multiple rows at once.

        Should apply transformations to all rows.
        """
        field_mappings = {
            "Name": "name",
            "Value": "value",
        }

        raw_data = [
            {"Name": "Item 1", "Value": "10"},
            {"Name": "Item 2", "Value": "20"},
        ]

        transformer = DataTransformer(field_mappings)
        result = transformer.transform(raw_data)

        assert len(result) == 2
        assert result[0]["name"] == "Item 1"
        assert result[1]["value"] == "20"

    def test_transform_with_custom_transformation(self):
        """
        Test transformer with custom transformation function.

        Should work with any callable transformation.
        """
        field_mappings = {
            "Number": "doubled",
        }

        # Custom transformation: double the number
        def double_number(value):
            try:
                return str(int(value) * 2)
            except (ValueError, TypeError):
                return "0"

        transformations = {
            "doubled": double_number,
        }

        raw_row = {
            "Number": "5",
        }

        transformer = DataTransformer(field_mappings, transformations)
        result = transformer.transform_row(raw_row)

        assert result["doubled"] == "10"


class TestPreserveLineBreaks:
    """Tests for preserve_line_breaks function."""

    def test_preserve_single_line(self):
        """
        Test with single line of text.

        Should return text unchanged (no line breaks to preserve).
        """
        result = preserve_line_breaks("Single line of text")

        assert result == "Single line of text"

    def test_preserve_multiple_lines(self):
        """
        Test with multiple lines separated by newlines.

        Should convert \\n to <br> tags.
        """
        result = preserve_line_breaks("Line 1\nLine 2\nLine 3")

        assert result == "Line 1<br>Line 2<br>Line 3"

    def test_preserve_empty_string(self):
        """
        Test with empty string.

        Should return empty string.
        """
        result = preserve_line_breaks("")

        assert result == ""

    def test_preserve_none_value(self):
        """
        Test with None value.

        Should return empty string.
        """
        result = preserve_line_breaks(None)

        assert result == ""

    def test_preserve_with_leading_trailing_whitespace(self):
        """
        Test that leading/trailing whitespace is stripped.

        Should strip outer whitespace but preserve line breaks.
        """
        result = preserve_line_breaks("  Line 1\nLine 2  ")

        assert result == "Line 1<br>Line 2"

    def test_preserve_windows_line_endings(self):
        """
        Test with Windows-style line endings (\\r\\n).

        Should handle \\r\\n correctly.
        """
        result = preserve_line_breaks("Line 1\r\nLine 2")

        # Python's replace will leave \r, which is fine for HTML
        # but let's be explicit about what we expect
        assert "Line 1" in result
        assert "Line 2" in result
        assert "<br>" in result
