"""
Unit tests for data validator.

Tests validation of reports data structure. The validator checks only
that data is structurally sound, NOT that content meets business rules.

Philosophy: Trust the data source. Report what exists.
"""

import pytest
from report_generator.data.validator import DataValidator


class TestDataValidator:
    """Test suite for DataValidator class."""

    def test_validate_valid_data(self):
        """
        Test validation of properly structured data.

        Should return valid=True with no errors.
        """
        valid_data = [
            {
                "L4 Deliverables": "Test Deliverable",
                "Deliverable Status": "On Track",
                "L4 Priority": "P0",
            }
        ]

        schema = {
            "expected_columns": ["L4 Deliverables", "Deliverable Status", "L4 Priority"]
        }

        validator = DataValidator()
        result = validator.validate(valid_data, schema)

        assert result["valid"] is True
        assert len(result["errors"]) == 0

    def test_validate_with_missing_expected_columns(self):
        """
        Test validation when expected columns are missing.

        Should return valid=True but include warnings about missing columns.
        Does NOT fail - just informs user.
        """
        data = [
            {
                "L4 Deliverables": "Test Deliverable",
                # Missing other expected columns
            }
        ]

        schema = {
            "expected_columns": ["L4 Deliverables", "Deliverable Status", "L4 Priority"]
        }

        validator = DataValidator()
        result = validator.validate(data, schema)

        # Still valid - missing columns don't cause failure
        assert result["valid"] is True

        # But should warn about missing columns
        assert len(result["warnings"]) > 0
        warning_text = " ".join(result["warnings"]).lower()
        assert "missing" in warning_text or "expected" in warning_text

    def test_validate_empty_data(self):
        """
        Test validation of empty data list.

        Should return valid=False - this is catastrophic, can't generate reports.
        """
        validator = DataValidator()
        result = validator.validate([], {})

        assert result["valid"] is False
        assert len(result["errors"]) > 0
        error_text = " ".join(result["errors"]).lower()
        assert "no data" in error_text or "empty" in error_text

    def test_validate_data_with_no_columns(self):
        """
        Test validation of data with empty dictionaries.

        Should return valid=False - no columns means broken structure.
        """
        invalid_data = [{}]  # Empty dictionary

        validator = DataValidator()
        result = validator.validate(invalid_data, {})

        assert result["valid"] is False
        assert len(result["errors"]) > 0

    def test_validate_accepts_any_status_value(self):
        """
        Test that validator accepts ANY status value.

        Philosophy: Trust Airtable. If they change pick list values,
        reports should still work. Template will display whatever value exists.
        """
        data = [
            {
                "L4 Deliverables": "Test",
                "Deliverable Status": "Brand New Status Not In Our List",
                "L4 Priority": "P0",
            }
        ]

        schema = {
            "expected_columns": ["L4 Deliverables", "Deliverable Status", "L4 Priority"]
        }

        validator = DataValidator()
        result = validator.validate(data, schema)

        # Should be valid - we accept any status value
        assert result["valid"] is True
        # Should have no errors about invalid status
        assert len(result["errors"]) == 0

    def test_validate_accepts_any_priority_value(self):
        """
        Test that validator accepts ANY priority value.

        Same philosophy as status - trust the data source.
        """
        data = [
            {
                "L4 Deliverables": "Test",
                "Deliverable Status": "On Track",
                "L4 Priority": "P99",  # Not a "standard" priority
            }
        ]

        schema = {
            "expected_columns": ["L4 Deliverables", "Deliverable Status", "L4 Priority"]
        }

        validator = DataValidator()
        result = validator.validate(data, schema)

        # Should be valid - we accept any priority value
        assert result["valid"] is True
        assert len(result["errors"]) == 0

    def test_validate_with_unexpected_columns(self):
        """
        Test validation when data has extra columns not in schema.

        Should be valid and provide info message (not warning or error).
        Extra columns are fine - they'll just be ignored.
        """
        data = [
            {
                "L4 Deliverables": "Test",
                "Deliverable Status": "On Track",
                "Extra Column 1": "Extra Data",
                "Extra Column 2": "More Extra",
            }
        ]

        schema = {"expected_columns": ["L4 Deliverables", "Deliverable Status"]}

        validator = DataValidator()
        result = validator.validate(data, schema)

        # Still valid
        assert result["valid"] is True

        # Should have info about unexpected columns
        assert len(result["info"]) > 0
        info_text = " ".join(result["info"]).lower()
        assert "unexpected" in info_text or "extra" in info_text

    def test_validate_with_empty_values(self):
        """
        Test that validator accepts rows with empty/None values.

        Empty values are fine - template will handle display.
        """
        data = [
            {
                "L4 Deliverables": "",
                "Deliverable Status": None,
                "L4 Priority": "P0",
            }
        ]

        schema = {
            "expected_columns": ["L4 Deliverables", "Deliverable Status", "L4 Priority"]
        }

        validator = DataValidator()
        result = validator.validate(data, schema)

        # Empty values don't cause validation failure
        assert result["valid"] is True
        assert len(result["errors"]) == 0

    def test_validate_without_schema(self):
        """
        Test validation when no schema is provided.

        Should still work - just won't check for expected columns.
        """
        data = [
            {
                "Any Column": "Any Value",
            }
        ]

        validator = DataValidator()
        result = validator.validate(data, schema_config=None)

        # Should be valid - no schema means no expectations to violate
        assert result["valid"] is True

    def test_validate_result_structure(self):
        """
        Test that validation result has expected structure.

        Result should always have: valid, errors, warnings, info
        """
        data = [{"Column": "Value"}]

        validator = DataValidator()
        result = validator.validate(data, {})

        # Check result structure
        assert "valid" in result
        assert "errors" in result
        assert "warnings" in result
        assert "info" in result

        # Check types
        assert isinstance(result["valid"], bool)
        assert isinstance(result["errors"], list)
        assert isinstance(result["warnings"], list)
        assert isinstance(result["info"], list)

    def test_validate_with_inconsistent_rows(self):
        """
        Test validation when rows have inconsistent columns.

        Should return valid=True but include warnings about inconsistent rows.
        """
        data = [
            {"Name": "Alice", "Age": 30, "City": "NYC"},
            {"Name": "Bob", "Age": 25},  # Missing City
            {"Name": "Carol", "Age": 28, "City": "LA", "Extra": "Data"},  # Extra column
        ]

        schema = {"expected_columns": ["Name", "Age", "City"]}

        validator = DataValidator()
        result = validator.validate(data, schema)

        # Still valid - inconsistent rows don't cause failure
        assert result["valid"] is True

        # But should warn about inconsistent rows
        assert len(result["warnings"]) > 0
        warning_text = " ".join(result["warnings"]).lower()
        assert "inconsistent" in warning_text


class TestCheckColumnConsistency:
    """Tests for the _check_column_consistency helper method."""

    def test_check_consistency_with_empty_data(self):
        """
        Test column consistency check with empty data.

        Should return empty list (no inconsistencies).
        """
        validator = DataValidator()
        result = validator._check_column_consistency([])

        assert result == []

    def test_check_consistency_with_single_row(self):
        """
        Test column consistency check with single row.

        Should return empty list (nothing to compare).
        """
        data = [{"Name": "Alice", "Age": 30}]

        validator = DataValidator()
        result = validator._check_column_consistency(data)

        assert result == []

    def test_check_consistency_with_consistent_rows(self):
        """
        Test column consistency check with all consistent rows.

        Should return empty list.
        """
        data = [
            {"Name": "Alice", "Age": 30},
            {"Name": "Bob", "Age": 25},
            {"Name": "Carol", "Age": 28},
        ]

        validator = DataValidator()
        result = validator._check_column_consistency(data)

        assert result == []

    def test_check_consistency_with_inconsistent_rows(self):
        """
        Test column consistency check with inconsistent rows.

        Should return list of row numbers (1-indexed) with inconsistencies.
        """
        data = [
            {"Name": "Alice", "Age": 30},
            {"Name": "Bob"},  # Missing Age - row 2
            {"Name": "Carol", "Age": 28},
            {"Name": "David", "Age": 35, "City": "NYC"},  # Extra column - row 4
        ]

        validator = DataValidator()
        result = validator._check_column_consistency(data)

        # Row 2 and 4 should be flagged
        assert 2 in result
        assert 4 in result
        assert len(result) == 2

    def test_check_consistency_multiple_inconsistent_rows(self):
        """
        Test column consistency with multiple inconsistent rows.
        """
        data = [
            {"A": 1, "B": 2, "C": 3},
            {"A": 1, "B": 2},  # Row 2 - missing C
            {"A": 1},  # Row 3 - missing B and C
            {"A": 1, "B": 2, "C": 3, "D": 4},  # Row 4 - extra D
        ]

        validator = DataValidator()
        result = validator._check_column_consistency(data)

        assert 2 in result
        assert 3 in result
        assert 4 in result
        assert len(result) == 3
