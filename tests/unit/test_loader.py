"""
Unit tests for CSV data loader.

Tests the loading and basic validation of CSV files containing
reports data.
"""

from pathlib import Path

import pytest

from report_generator.data.loader import TabularDataLoader


class TestTabularDataLoader:
    """Test suite for TabularDataLoader class."""

    def test_load_valid_csv(self):
        """
        Test loading a valid CSV file.

        Should successfully load the mock data and return a list of dicts.
        """
        loader = TabularDataLoader()
        csv_path = Path("tests/fixtures/mock_data.csv")

        data = loader.load(csv_path)

        # Basic assertions
        assert data is not None
        assert len(data) == 5  # Mock data has 5 rows
        assert isinstance(data, list)
        assert isinstance(data[0], dict)

    def test_load_csv_has_required_columns(self):
        """
        Test that loaded data contains required columns.

        Validates that all critical columns are present after loading.
        """
        loader = TabularDataLoader()
        csv_path = Path("tests/fixtures/mock_data.csv")

        data = loader.load(csv_path)
        first_row = data[0]

        # Check for required columns
        required_columns = [
            "L4 Deliverables",
            "Deliverable Status",
            "L4 Priority",
            "Engineering Workstream Lead",
        ]

        for column in required_columns:
            assert column in first_row, f"Missing required column: {column}"

    def test_load_nonexistent_file(self):
        """
        Test error handling for non-existent file.

        Should raise FileNotFoundError with helpful message.
        """
        loader = TabularDataLoader()
        fake_path = Path("tests/fixtures/nonexistent.csv")

        with pytest.raises(FileNotFoundError) as exc_info:
            loader.load(fake_path)

        assert "not found" in str(exc_info.value).lower()

    def test_load_empty_csv(self):
        """
        Test handling of empty CSV file.

        Should raise ValueError indicating no data.
        """
        # Create empty CSV for testing
        empty_csv = Path("tests/fixtures/empty.csv")
        empty_csv.write_text("")

        loader = TabularDataLoader()

        with pytest.raises(ValueError) as exc_info:
            loader.load(empty_csv)

        assert "empty" in str(exc_info.value).lower()

        # Cleanup
        empty_csv.unlink()

    def test_load_tsv_file(self):
        """
        Test loading a TSV (tab-separated) file.

        Should successfully load tab-delimited data.
        """
        # Create a simple TSV
        tsv_path = Path("tests/fixtures/test.tsv")
        tsv_path.write_text("Name\tAge\tCity\nAlice\t30\tNYC\nBob\t25\tLA")

        loader = TabularDataLoader()
        data = loader.load(tsv_path)

        assert len(data) == 2
        assert data[0]["Name"] == "Alice"
        assert data[0]["Age"] == 30
        assert data[1]["City"] == "LA"

        # Cleanup
        tsv_path.unlink()

    def test_load_csv_with_bom(self):
        """
        Test loading CSV with UTF-8 BOM (Byte Order Mark).

        Some systems (especially Windows Excel and Airtable exports) add a BOM
        to CSV files. The loader should handle this gracefully so that column
        names are read correctly without the BOM character.

        Without proper encoding handling, the BOM appears in the first column
        name, breaking all column lookups.
        """
        # Create CSV with BOM (byte order mark)
        # UTF-8 BOM is \ufeff - it should be invisible when loaded correctly
        bom_csv = Path("tests/fixtures/bom.csv")
        bom_csv.write_text("\ufeffName,Age,City\nAlice,30,NYC\nBob,25,LA", encoding="utf-8-sig")

        loader = TabularDataLoader()
        data = loader.load(bom_csv)

        # Column name should NOT have BOM character
        # If BOM handling is broken, first column would be '\ufeffName'
        assert "Name" in data[0], "BOM not handled - column name is mangled"
        assert "\ufeffName" not in data[0], "BOM character present in column name"

        # Verify data loaded correctly
        assert len(data) == 2
        assert data[0]["Name"] == "Alice"
        assert data[1]["City"] == "LA"

        # Cleanup
        bom_csv.unlink()

    def test_load_invalid_file_extension(self):
        """
        Test error handling for invalid file extension.

        Should raise ValueError for non-CSV/TSV files.
        """
        # Create a file with invalid extension
        invalid_file = Path("tests/fixtures/test.json")
        invalid_file.write_text('{"name": "test"}')

        loader = TabularDataLoader()

        with pytest.raises(ValueError) as exc_info:
            loader.load(invalid_file)

        assert "invalid file type" in str(exc_info.value).lower()
        assert ".json" in str(exc_info.value)

        # Cleanup
        invalid_file.unlink()

    def test_load_txt_file_allowed(self):
        """
        Test that .txt files are accepted as valid input.

        Some tools export CSV data with .txt extension.
        """
        txt_path = Path("tests/fixtures/test_data.txt")
        txt_path.write_text("Name,Age,City\nAlice,30,NYC\nBob,25,LA")

        loader = TabularDataLoader()
        data = loader.load(txt_path)

        assert len(data) == 2
        assert data[0]["Name"] == "Alice"

        # Cleanup
        txt_path.unlink()

    def test_load_malformed_csv_binary(self):
        """
        Test error handling for binary/corrupted file.

        Should raise ValueError with helpful message.
        """
        malformed_csv = Path("tests/fixtures/malformed.csv")
        malformed_csv.write_bytes(b"\x00\x01\x02\x03")

        loader = TabularDataLoader()

        with pytest.raises(ValueError) as exc_info:
            loader.load(malformed_csv)

        # Cleanup
        malformed_csv.unlink()

    def test_load_parser_error(self):
        """
        Test error handling for ParserError.

        Should raise ValueError when pandas can't parse the file.
        """
        from unittest.mock import patch

        import pandas as pd

        # Create a normal CSV file
        parser_error_csv = Path("tests/fixtures/parser_error.csv")
        parser_error_csv.write_text("Name,Age,City\nAlice,30,NYC")

        loader = TabularDataLoader()

        # Mock pandas.read_csv to raise ParserError
        with patch("pandas.read_csv", side_effect=pd.errors.ParserError("Test parser error")):
            with pytest.raises(ValueError) as exc_info:
                loader.load(parser_error_csv)

            assert "malformed" in str(exc_info.value).lower()

        # Cleanup
        parser_error_csv.unlink()

    def test_load_generic_exception(self):
        """
        Test error handling for generic exceptions during file reading.

        Should raise ValueError with the original error message.
        """
        from unittest.mock import patch

        # Create a normal CSV file
        generic_error_csv = Path("tests/fixtures/generic_error.csv")
        generic_error_csv.write_text("Name,Age,City\nAlice,30,NYC")

        loader = TabularDataLoader()

        # Mock pandas.read_csv to raise a generic exception
        with patch("pandas.read_csv", side_effect=Exception("Generic read error")):
            with pytest.raises(ValueError) as exc_info:
                loader.load(generic_error_csv)

            assert "error reading file" in str(exc_info.value).lower()
            assert "Generic read error" in str(exc_info.value)

        # Cleanup
        generic_error_csv.unlink()

    def test_load_header_only_csv(self):
        """
        Test handling of CSV with header but no data rows.

        Should raise ValueError indicating no data.
        """
        header_only = Path("tests/fixtures/header_only.csv")
        header_only.write_text("Name,Age,City\n")

        loader = TabularDataLoader()

        with pytest.raises(ValueError) as exc_info:
            loader.load(header_only)

        assert "no data" in str(exc_info.value).lower()

        # Cleanup
        header_only.unlink()

    def test_load_too_few_columns(self):
        """
        Test handling of CSV with too few columns.

        Files with fewer than 3 columns are likely malformed.
        """
        few_columns = Path("tests/fixtures/few_columns.csv")
        few_columns.write_text("Name,Age\nAlice,30\nBob,25")

        loader = TabularDataLoader()

        with pytest.raises(ValueError) as exc_info:
            loader.load(few_columns)

        assert "malformed" in str(exc_info.value).lower()
        assert "3" in str(exc_info.value)  # Should mention expected columns

        # Cleanup
        few_columns.unlink()

    def test_load_with_string_path(self):
        """
        Test that string paths work as well as Path objects.
        """
        loader = TabularDataLoader()

        # Use string path instead of Path object
        data = loader.load("tests/fixtures/mock_data.csv")

        assert data is not None
        assert len(data) > 0
