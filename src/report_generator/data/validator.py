"""
Data validator for reports generator.

This module validates that loaded data has basic structural integrity.
It does NOT enforce business rules or validate content values.

Philosophy: Trust the data source. Report what exists.
The validator checks structure only - templates handle missing/incomplete data.
"""

from typing import Any, Dict, List


class DataValidator:  # pylint: disable=too-few-public-methods
    """
    Validates reports data structure (not content).

    This class performs lightweight validation to ensure data can be
    processed. It does NOT validate business rules like required fields
    or valid enum values - that's the data source's responsibility.

    The validator returns warnings for unexpected structure but only
    fails for catastrophic issues (empty data, no columns).

    Example:
        >>> validator = DataValidator()
        >>> schema = {'expected_columns': ['Name', 'Status']}
        >>> result = validator.validate(data, schema)
        >>> if not result['valid']:
        ...     print(f"Errors: {result['errors']}")
        >>> if result['warnings']:
        ...     print(f"Warnings: {result['warnings']}")
    """

    def validate(self, data: List[Dict[str, Any]], schema_config: dict = None) -> dict:
        """
        Validate data structure and return result with errors/warnings.

        Only fails (valid=False) for catastrophic issues:
        - Empty data (can't generate reports with no data)
        - Data has no columns (completely broken structure)

        Returns warnings (but valid=True) for:
        - Missing expected columns (template will handle empty values)
        - Unexpected columns (will be ignored)

        Args:
            data: List of dictionaries representing reports rows
            schema_config: Optional dictionary with 'expected_columns' list

        Returns:
            Dictionary with structure:
            {
                'valid': bool,           # False only for catastrophic failures
                'errors': List[str],     # Catastrophic issues
                'warnings': List[str],   # Structure issues (non-fatal)
                'info': List[str]        # Informational messages
            }

        Example:
            >>> validator = DataValidator()
            >>> schema = {
            ...     'expected_columns': ['Name', 'Age', 'City']
            ... }
            >>> data = [{'Name': 'Alice', 'Age': 30}]
            >>> result = validator.validate(data, schema)
            >>> print(result['valid'])  # True - missing columns don't fail
            True
            >>> print(result['warnings'])  # Warns about missing 'City'
            ["Missing expected columns: City"]
        """
        schema_config = schema_config or {}

        result = {"valid": True, "errors": [], "warnings": [], "info": []}

        # Catastrophic check: No data at all
        if not data or len(data) == 0:
            result["valid"] = False
            result["errors"].append(
                "No data to validate. " "The data list is empty - cannot generate reports."
            )
            return result

        # Catastrophic check: Data exists but has no columns
        first_row = data[0]
        if not first_row or len(first_row) == 0:
            result["valid"] = False
            result["errors"].append(
                "Data has no columns. " "The data structure is broken - cannot generate reports."
            )
            return result

        # Non-catastrophic checks: Structure warnings
        expected_columns = set(schema_config.get("expected_columns", []))
        actual_columns = set(first_row.keys())

        # Check for missing expected columns
        missing_columns = expected_columns - actual_columns
        if missing_columns:
            result["warnings"].append(
                f"Missing expected columns: {', '.join(sorted(missing_columns))}"
            )
            result["info"].append(
                "Report will handle missing data by showing empty values or placeholders."
            )

        # Check for unexpected columns (informational only)
        unexpected_columns = actual_columns - expected_columns
        if unexpected_columns and expected_columns:  # Only if we have expectations
            unexpected_list = ", ".join(sorted(unexpected_columns))
            result["info"].append(f"Found unexpected columns (will be ignored): {unexpected_list}")

        # Check data consistency across rows (optional - informational)
        if len(data) > 1:
            inconsistent_rows = self._check_column_consistency(data)
            if inconsistent_rows:
                result["warnings"].append(
                    f"Some rows have inconsistent columns. "
                    f"Rows with issues: {', '.join(map(str, inconsistent_rows))}"
                )
                result["info"].append("This may indicate data quality issues in the source.")

        return result

    def _check_column_consistency(self, data: List[Dict[str, Any]]) -> List[int]:
        """
        Check if all rows have the same columns.

        Returns list of row numbers (1-indexed) that have different columns
        than the first row.

        Args:
            data: List of dictionaries

        Returns:
            List of row numbers with inconsistent columns (empty if all consistent)
        """
        if not data:
            return []

        first_row_columns = set(data[0].keys())
        inconsistent = []

        for i, row in enumerate(data[1:], start=2):  # Start at row 2
            if set(row.keys()) != first_row_columns:
                inconsistent.append(i)

        return inconsistent
