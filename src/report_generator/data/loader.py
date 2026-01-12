"""
CSV data loader for reports generator.

This module handles loading CSV files containing reports data and
converting them into Python dictionaries for processing.

Supports both comma-separated (CSV) and tab-separated (TSV) files.
"""

from pathlib import Path
import pandas as pd


class TabularDataLoader:  # pylint: disable=too-few-public-methods
    """
    Loads CSV/TSV files and converts them to dictionaries.

    This class handles the initial data loading from delimited text files,
    including basic validation and error handling. It automatically detects
    whether the file uses comma or tab delimiters.

    Example:
        >>> loader = TabularDataLoader()
        >>> data = loader.load("data/reports.csv")
        >>> print(f"Loaded {len(data)} rows")
    """

    def load(self, filepath):
        """
        Load a CSV or TSV file and return data as list of dictionaries.

        Each row in the file becomes a dictionary with column names as keys.
        The file is expected to have a header row with column names.
        Automatically detects comma or tab delimiters.

        Args:
            filepath: Path to the CSV/TSV file to load.
                     Can be either a Path object or string path.

        Returns:
            List of dictionaries, where each dict represents one row.
            Keys are column names, values are cell values.

        Raises:
            FileNotFoundError: If the specified file doesn't exist
            ValueError: If the file is empty, malformed, or wrong file type

        Example:
            >>> loader = TabularDataLoader()
            >>> data = loader.load("data/reports.csv")
            >>> print(data[0]["L4 Deliverables"])
            "User Authentication Enhancement"
        """
        # Convert to Path object if string
        filepath = Path(filepath)

        # Check file exists
        if not filepath.exists():
            raise FileNotFoundError(
                f"CSV file not found: {filepath}\n"
                f"Please check the file path and try again."
            )

        # Validate file extension
        # Accept .csv, .tsv, and .txt (common export formats)
        valid_extensions = {".csv", ".tsv", ".txt"}
        if filepath.suffix.lower() not in valid_extensions:
            raise ValueError(
                f"Invalid file type: {filepath.suffix}\n"
                f"Expected a CSV or TSV file (.csv, .tsv, or .txt), but got: {filepath.name}\n"
                f"Please provide a delimited text file."
            )

        # Determine delimiter based on file extension
        # .tsv files use tabs, others default to comma but pandas will auto-detect
        if filepath.suffix.lower() == ".tsv":
            delimiter = "\t"
        else:
            # Let pandas auto-detect (handles both comma and tab)
            delimiter = ","

        # Load file with pandas
        try:
            df = pd.read_csv(filepath, sep=delimiter, encoding="utf-8-sig")
        except pd.errors.EmptyDataError as exc:
            raise ValueError(
                f"File is empty: {filepath}\n"
                f"The file must contain a header row and at least one data row."
            ) from exc
        except pd.errors.ParserError as exc:
            raise ValueError(
                f"File is malformed: {filepath}\n"
                f"The file could not be parsed as valid delimited data.\n"
                f"Error: {exc}\n"
                "Please check that the file uses comma or tab delimiters "
                "and has consistent columns."
            ) from exc
        except Exception as exc:
            raise ValueError(
                f"Error reading file: {filepath}\nError: {exc}"
            ) from exc

        # Check if DataFrame is empty
        if df.empty:
            raise ValueError(
                f"File contains no data: {filepath}\n"
                f"The file must contain at least one data row."
            )

        # Validate minimum structure
        # File should have at least a few columns (realistic reports data)
        min_columns = 3
        if len(df.columns) < min_columns:
            raise ValueError(
                f"File appears to be malformed: {filepath}\n"
                f"Expected at least {min_columns} columns, but found {len(df.columns)}.\n"
                f"Columns found: {list(df.columns)}\n"
                f"Please check that the file uses comma or tab delimiters."
            )

        # Convert to list of dictionaries
        data = df.to_dict("records")

        return data
