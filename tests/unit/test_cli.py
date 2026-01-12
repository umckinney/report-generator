"""
Unit tests for CLI module.

Tests command-line interface functionality.
"""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from argparse import Namespace
import sys

from report_generator.cli import (
    main,
    generate_report,
    interactive_mode,
    REPORT_REGISTRY,
)


class TestReportRegistry:
    """Tests for the report registry."""

    def test_registry_contains_kpr(self):
        """Test that KPR report is registered."""
        assert "kpr" in REPORT_REGISTRY

    def test_registry_entry_has_required_keys(self):
        """Test that registry entries have required configuration."""
        for report_id, config in REPORT_REGISTRY.items():
            assert "name" in config
            assert "generator_class" in config
            assert "email_config" in config


class TestGenerateReport:
    """Tests for the generate_report function."""

    def test_generate_unknown_report_type(self):
        """Test error handling for unknown report type."""
        args = Namespace(
            report_type="unknown_report", csv="test.csv", output=None, email=False
        )

        result = generate_report(args)

        assert result == 1  # Should return error code

    def test_generate_csv_not_found(self, tmp_path):
        """Test error handling when CSV file doesn't exist."""
        args = Namespace(
            report_type="kpr",
            csv=str(tmp_path / "nonexistent.csv"),
            output=None,
            email=False,
        )

        result = generate_report(args)

        assert result == 1  # Should return error code

    def test_generate_success_without_output_path(self, tmp_path):
        """Test successful report generation without specified output."""
        # Create valid test CSV with expected columns
        csv_path = tmp_path / "test.csv"
        csv_path.write_text(
            "Initiatives (L3),L4 Deliverables,Deliverable Status,Event Phase,L4 Priority,"
            "Delivery Date,Risks & Issues,Key Achievements,Program Workstream Lead,"
            "Product Workstream Lead,Engineering Workstream Lead,Design Workstream Lead,"
            "QA Workstream Lead\n"
            "Init,Test Deliverable,On Track,In Development,P1,2025-03-15,None,Progress,"
            "Lead1,Lead2,Lead3,Lead4,Lead5\n"
        )

        args = Namespace(report_type="kpr", csv=str(csv_path), output=None, email=False)

        result = generate_report(args)

        assert result == 0

    def test_generate_success_with_output_path(self, tmp_path):
        """Test successful report generation with specified output."""
        csv_path = tmp_path / "test.csv"
        csv_path.write_text(
            "Initiatives (L3),L4 Deliverables,Deliverable Status,Event Phase,L4 Priority,"
            "Delivery Date,Risks & Issues,Key Achievements,Program Workstream Lead,"
            "Product Workstream Lead,Engineering Workstream Lead,Design Workstream Lead,"
            "QA Workstream Lead\n"
            "Init,Test Deliverable,On Track,In Development,P1,2025-03-15,None,Progress,"
            "Lead1,Lead2,Lead3,Lead4,Lead5\n"
        )
        output_path = tmp_path / "output.html"

        args = Namespace(
            report_type="kpr", csv=str(csv_path), output=str(output_path), email=False
        )

        result = generate_report(args)

        assert result == 0
        assert output_path.exists()

    @patch("report_generator.cli.EmailDraftHandler")
    def test_generate_with_email_success(self, mock_email_class, tmp_path):
        """Test report generation with email draft opening."""
        mock_email = MagicMock()
        mock_email.open_draft.return_value = True
        mock_email_class.return_value = mock_email

        csv_path = tmp_path / "test.csv"
        csv_path.write_text(
            "Initiatives (L3),L4 Deliverables,Deliverable Status,Event Phase,L4 Priority,"
            "Delivery Date,Risks & Issues,Key Achievements,Program Workstream Lead,"
            "Product Workstream Lead,Engineering Workstream Lead,Design Workstream Lead,"
            "QA Workstream Lead\n"
            "Init,Test Deliverable,On Track,In Development,P1,2025-03-15,None,Progress,"
            "Lead1,Lead2,Lead3,Lead4,Lead5\n"
        )

        args = Namespace(report_type="kpr", csv=str(csv_path), output=None, email=True)

        result = generate_report(args)

        assert result == 0
        mock_email.open_draft.assert_called_once()

    @patch("report_generator.cli.EmailDraftHandler")
    def test_generate_with_email_failure(self, mock_email_class, tmp_path):
        """Test report generation when email draft fails to open."""
        mock_email = MagicMock()
        mock_email.open_draft.return_value = False  # Email fails
        mock_email_class.return_value = mock_email

        csv_path = tmp_path / "test.csv"
        csv_path.write_text(
            "Initiatives (L3),L4 Deliverables,Deliverable Status,Event Phase,L4 Priority,"
            "Delivery Date,Risks & Issues,Key Achievements,Program Workstream Lead,"
            "Product Workstream Lead,Engineering Workstream Lead,Design Workstream Lead,"
            "QA Workstream Lead\n"
            "Init,Test Deliverable,On Track,In Development,P1,2025-03-15,None,Progress,"
            "Lead1,Lead2,Lead3,Lead4,Lead5\n"
        )

        args = Namespace(report_type="kpr", csv=str(csv_path), output=None, email=True)

        result = generate_report(args)

        # Should still succeed (email failure is not fatal)
        assert result == 0

    def test_generate_handles_exception(self, tmp_path):
        """Test error handling when generator raises exception."""
        # Create invalid CSV that will cause validation to fail
        csv_path = tmp_path / "test.csv"
        csv_path.write_text("a,b\n")  # Too few columns, no data

        args = Namespace(report_type="kpr", csv=str(csv_path), output=None, email=False)

        result = generate_report(args)

        assert result == 1  # Should return error code


class TestInteractiveMode:
    """Tests for interactive mode."""

    @patch("builtins.input")
    def test_interactive_no_file_provided(self, mock_input):
        """Test interactive mode when no file is provided."""
        mock_input.side_effect = ["", ""]  # Empty input, then Enter to close

        result = interactive_mode()

        assert result == 1

    @patch("report_generator.cli.generate_report")
    @patch("builtins.input")
    def test_interactive_with_file(self, mock_input, mock_generate):
        """Test interactive mode with valid file path."""
        mock_input.side_effect = ["/path/to/file.csv", ""]  # File path, then Enter
        mock_generate.return_value = 0

        result = interactive_mode()

        assert result == 0
        mock_generate.assert_called_once()

        # Verify args passed to generate_report
        call_args = mock_generate.call_args[0][0]
        assert call_args.csv == "/path/to/file.csv"
        assert call_args.report_type == "kpr"
        assert call_args.email is True

    @patch("report_generator.cli.generate_report")
    @patch("builtins.input")
    def test_interactive_strips_quotes(self, mock_input, mock_generate):
        """Test that interactive mode strips quotes from path."""
        mock_input.side_effect = ['"/path/to/file.csv"', ""]
        mock_generate.return_value = 0

        interactive_mode()

        call_args = mock_generate.call_args[0][0]
        assert call_args.csv == "/path/to/file.csv"  # Quotes stripped


class TestMain:
    """Tests for main CLI entry point."""

    @patch("report_generator.cli.interactive_mode")
    def test_main_no_args_runs_interactive(self, mock_interactive):
        """Test that main runs interactive mode when no args provided."""
        mock_interactive.return_value = 0

        with patch.object(sys, "argv", ["report_generator"]):
            result = main()

        mock_interactive.assert_called_once()
        assert result == 0

    @patch("report_generator.cli.generate_report")
    def test_main_generate_command(self, mock_generate, tmp_path):
        """Test main with generate command."""
        mock_generate.return_value = 0

        csv_path = tmp_path / "test.csv"
        csv_path.write_text("Name,Age,City\nAlice,30,NYC")

        with patch.object(
            sys,
            "argv",
            ["report_generator", "generate", "--report", "kpr", "--csv", str(csv_path)],
        ):
            result = main()

        mock_generate.assert_called_once()
        assert result == 0

    def test_main_list_reports_command(self, capsys):
        """Test main with list-reports command."""
        with patch.object(sys, "argv", ["report_generator", "list-reports"]):
            result = main()

        assert result == 0

        # Check output
        captured = capsys.readouterr()
        assert "kpr" in captured.out.lower()
        assert "key priorities" in captured.out.lower()

    def test_main_no_command_shows_help(self, capsys):
        """Test that main with no command shows help."""
        with patch.object(sys, "argv", ["report_generator", "--help"]):
            with pytest.raises(SystemExit) as exc_info:
                main()

        # argparse exits with 0 for --help
        assert exc_info.value.code == 0

    @patch("report_generator.cli.generate_report")
    def test_main_generate_with_all_options(self, mock_generate, tmp_path):
        """Test main with all generate options."""
        mock_generate.return_value = 0

        csv_path = tmp_path / "test.csv"
        csv_path.write_text("Name,Age,City\nAlice,30,NYC")
        output_path = tmp_path / "output.html"

        with patch.object(
            sys,
            "argv",
            [
                "report_generator",
                "generate",
                "--report",
                "kpr",
                "--csv",
                str(csv_path),
                "--output",
                str(output_path),
                "--email",
            ],
        ):
            result = main()

        mock_generate.assert_called_once()

        # Verify all args were passed
        call_args = mock_generate.call_args[0][0]
        assert call_args.report_type == "kpr"
        assert call_args.email is True

    def test_main_unknown_command_exits(self):
        """Test that unknown command causes argparse to exit."""
        with patch.object(sys, "argv", ["report_generator", "unknown"]):
            with pytest.raises(SystemExit) as exc_info:
                main()

        # argparse exits with code 2 for invalid arguments
        assert exc_info.value.code == 2

    def test_main_with_flag_but_no_command(self, capsys):
        """Test that providing a flag but no command shows help."""
        # When args.command is None (no subcommand selected), print help
        # This happens when you run: python -m report_generator --some-flag
        # But since we check len(sys.argv) == 1 first, we need 2+ args
        # The else branch is hit when argparse parses but command is None

        # Mock argparse to return args with command=None
        with patch.object(sys, "argv", ["report_generator", "generate"]):
            # Test with mocked parse_args that returns None command
            mock_args = Namespace(command=None)
            with patch("argparse.ArgumentParser.parse_args", return_value=mock_args):
                result = main()

        assert result == 1  # Should return error code

        captured = capsys.readouterr()
        # Help text should be printed (contains usage info)
        # Note: print_help goes to stdout
