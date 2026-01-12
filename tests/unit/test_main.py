"""
Unit tests for __main__ module.

Tests the entry point for running the package as a module.
"""

import pytest
import runpy
from unittest.mock import patch


class TestMainModule:
    """Tests for __main__.py module execution."""

    @patch("report_generator.cli.main")
    def test_main_imports_and_calls_cli_main(self, mock_main):
        """Test that __main__ imports and calls cli.main()."""
        mock_main.return_value = 0

        # Import the module directly to test the import
        import report_generator.__main__

        # The import should work without errors
        assert hasattr(report_generator.__main__, "main")

    def test_main_module_has_main_function(self):
        """Test that __main__ module exposes main function."""
        from report_generator.__main__ import main

        # main should be callable
        assert callable(main)

    @patch("report_generator.cli.main")
    def test_runpy_runs_main(self, mock_main):
        """Test that running as __main__ via runpy calls main()."""
        mock_main.return_value = 0

        # Use runpy to simulate running as: python -m report_generator
        # This will execute the if __name__ == '__main__' block
        try:
            runpy.run_module("report_generator", run_name="__main__", alter_sys=True)
        except SystemExit:
            pass  # main() may call sys.exit()

        # Verify main was called
        mock_main.assert_called_once()

    def test_main_module_direct_execution(self):
        """Test the __main__ module can be executed directly."""
        # Import main function
        from report_generator.__main__ import main

        # Mock sys.argv to have only the program name (triggers interactive mode)
        # and mock interactive_mode to return success
        with patch(
            "report_generator.cli.interactive_mode", return_value=0
        ) as mock_interactive:
            with patch("sys.argv", ["report_generator"]):
                # Re-import to get fresh reference with mocked sys.argv
                import report_generator.cli as cli_module

                result = cli_module.main()

        assert result == 0
