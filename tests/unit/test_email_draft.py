"""
Unit tests for email draft handler.

Tests the email draft functionality (without actually opening mail client).
"""

import pytest
from unittest.mock import patch, MagicMock, mock_open
from report_generator.output.email_draft import EmailDraftHandler


class TestEmailDraftHandler:
    """Tests for EmailDraftHandler class."""

    def test_handler_initialization(self):
        """Test that handler initializes correctly."""
        handler = EmailDraftHandler()

        assert handler is not None
        assert handler.platform is not None

    def test_handler_stores_platform(self):
        """Test that handler stores the current platform."""
        with patch("sys.platform", "darwin"):
            handler = EmailDraftHandler()
            assert handler.platform == "darwin"

        with patch("sys.platform", "linux"):
            handler = EmailDraftHandler()
            assert handler.platform == "linux"


class TestOpenDraft:
    """Tests for the open_draft method."""

    @patch("report_generator.output.email_draft.EmailDraftHandler._open_eml_draft")
    def test_open_draft_uses_eml_on_darwin(self, mock_eml):
        """Test that darwin platform uses EML draft approach."""
        mock_eml.return_value = True

        handler = EmailDraftHandler()
        handler.platform = "darwin"

        result = handler.open_draft(
            html_content="<h1>Test</h1>",
            subject="Test Subject",
            to_addresses=["test@example.com"],
        )

        assert result is True
        mock_eml.assert_called_once()

    @patch("report_generator.output.email_draft.EmailDraftHandler._open_in_browser")
    def test_open_draft_falls_back_to_browser_on_linux(self, mock_browser):
        """Test that non-darwin platforms fall back to browser."""
        mock_browser.return_value = True

        handler = EmailDraftHandler()
        handler.platform = "linux"

        result = handler.open_draft(
            html_content="<h1>Test</h1>", subject="Test Subject"
        )

        assert result is True
        mock_browser.assert_called_once_with("<h1>Test</h1>")

    @patch("report_generator.output.email_draft.EmailDraftHandler._open_in_browser")
    def test_open_draft_falls_back_to_browser_on_windows(self, mock_browser):
        """Test that Windows falls back to browser."""
        mock_browser.return_value = True

        handler = EmailDraftHandler()
        handler.platform = "win32"

        result = handler.open_draft(html_content="<h1>Test</h1>")

        assert result is True
        mock_browser.assert_called_once()

    def test_open_draft_handles_none_addresses(self):
        """Test that None addresses are converted to empty lists."""
        handler = EmailDraftHandler()
        handler.platform = "darwin"

        with patch.object(handler, "_open_eml_draft", return_value=True) as mock_eml:
            handler.open_draft(
                html_content="<h1>Test</h1>", to_addresses=None, cc_addresses=None
            )

            # Verify empty lists were passed
            call_args = mock_eml.call_args
            assert call_args[0][2] == []  # to_addresses
            assert call_args[0][3] == []  # cc_addresses


class TestOpenEmlDraft:
    """Tests for the _open_eml_draft method."""

    @patch("subprocess.run")
    @patch("tempfile.NamedTemporaryFile")
    def test_eml_draft_creates_file_and_opens(self, mock_tempfile, mock_run):
        """Test that EML draft creates temp file and opens it."""
        # Setup mock temp file
        mock_file = MagicMock()
        mock_file.name = "/tmp/test.eml"
        mock_file.__enter__ = MagicMock(return_value=mock_file)
        mock_file.__exit__ = MagicMock(return_value=False)
        mock_tempfile.return_value = mock_file

        handler = EmailDraftHandler()
        result = handler._open_eml_draft(
            html_content="<h1>Test</h1>",
            subject="Test Subject",
            to_addresses=["test@example.com"],
            cc_addresses=[],
        )

        assert result is True
        mock_run.assert_called_once_with(["open", "/tmp/test.eml"], check=False)

    @patch("subprocess.run")
    @patch("tempfile.NamedTemporaryFile")
    def test_eml_draft_includes_subject(self, mock_tempfile, mock_run):
        """Test that EML draft includes subject in email."""
        mock_file = MagicMock()
        mock_file.name = "/tmp/test.eml"
        mock_file.__enter__ = MagicMock(return_value=mock_file)
        mock_file.__exit__ = MagicMock(return_value=False)
        mock_tempfile.return_value = mock_file

        # Capture what's written to the file
        written_content = []
        mock_file.write = lambda x: written_content.append(x)

        handler = EmailDraftHandler()
        handler._open_eml_draft(
            html_content="<h1>Test</h1>",
            subject="My Test Subject",
            to_addresses=[],
            cc_addresses=[],
        )

        # Verify subject is in the written content
        content = b"".join(written_content).decode("utf-8")
        assert "Subject: My Test Subject" in content

    @patch("subprocess.run")
    @patch("tempfile.NamedTemporaryFile")
    def test_eml_draft_includes_to_addresses(self, mock_tempfile, mock_run):
        """Test that EML draft includes To addresses."""
        mock_file = MagicMock()
        mock_file.name = "/tmp/test.eml"
        mock_file.__enter__ = MagicMock(return_value=mock_file)
        mock_file.__exit__ = MagicMock(return_value=False)
        mock_tempfile.return_value = mock_file

        written_content = []
        mock_file.write = lambda x: written_content.append(x)

        handler = EmailDraftHandler()
        handler._open_eml_draft(
            html_content="<h1>Test</h1>",
            subject="Test",
            to_addresses=["alice@example.com", "bob@example.com"],
            cc_addresses=[],
        )

        content = b"".join(written_content).decode("utf-8")
        assert "To: alice@example.com, bob@example.com" in content

    @patch("subprocess.run")
    @patch("tempfile.NamedTemporaryFile")
    def test_eml_draft_includes_cc_addresses(self, mock_tempfile, mock_run):
        """Test that EML draft includes CC addresses."""
        mock_file = MagicMock()
        mock_file.name = "/tmp/test.eml"
        mock_file.__enter__ = MagicMock(return_value=mock_file)
        mock_file.__exit__ = MagicMock(return_value=False)
        mock_tempfile.return_value = mock_file

        written_content = []
        mock_file.write = lambda x: written_content.append(x)

        handler = EmailDraftHandler()
        handler._open_eml_draft(
            html_content="<h1>Test</h1>",
            subject="Test",
            to_addresses=["to@example.com"],
            cc_addresses=["cc1@example.com", "cc2@example.com"],
        )

        content = b"".join(written_content).decode("utf-8")
        assert "Cc: cc1@example.com, cc2@example.com" in content

    @patch("subprocess.run")
    @patch("tempfile.NamedTemporaryFile")
    def test_eml_draft_includes_html_content(self, mock_tempfile, mock_run):
        """Test that EML draft includes HTML content."""
        mock_file = MagicMock()
        mock_file.name = "/tmp/test.eml"
        mock_file.__enter__ = MagicMock(return_value=mock_file)
        mock_file.__exit__ = MagicMock(return_value=False)
        mock_tempfile.return_value = mock_file

        written_content = []
        mock_file.write = lambda x: written_content.append(x)

        handler = EmailDraftHandler()
        handler._open_eml_draft(
            html_content="<h1>My Report Content</h1>",
            subject="Test",
            to_addresses=[],
            cc_addresses=[],
        )

        content = b"".join(written_content).decode("utf-8")
        assert "<h1>My Report Content</h1>" in content

    @patch("subprocess.run")
    @patch("tempfile.NamedTemporaryFile")
    def test_eml_draft_includes_plaintext_fallback(self, mock_tempfile, mock_run):
        """Test that EML draft includes plain-text fallback message."""
        mock_file = MagicMock()
        mock_file.name = "/tmp/test.eml"
        mock_file.__enter__ = MagicMock(return_value=mock_file)
        mock_file.__exit__ = MagicMock(return_value=False)
        mock_tempfile.return_value = mock_file

        written_content = []
        mock_file.write = lambda x: written_content.append(x)

        handler = EmailDraftHandler()
        handler._open_eml_draft(
            html_content="<h1>Test</h1>",
            subject="Test",
            to_addresses=[],
            cc_addresses=[],
        )

        content = b"".join(written_content).decode("utf-8")
        assert "This message includes an HTML report" in content

    @patch("subprocess.run")
    @patch("tempfile.NamedTemporaryFile")
    def test_eml_draft_handles_empty_subject(self, mock_tempfile, mock_run):
        """Test that EML draft handles empty subject gracefully."""
        mock_file = MagicMock()
        mock_file.name = "/tmp/test.eml"
        mock_file.__enter__ = MagicMock(return_value=mock_file)
        mock_file.__exit__ = MagicMock(return_value=False)
        mock_tempfile.return_value = mock_file

        written_content = []
        mock_file.write = lambda x: written_content.append(x)

        handler = EmailDraftHandler()
        result = handler._open_eml_draft(
            html_content="<h1>Test</h1>",
            subject="",  # Empty subject
            to_addresses=[],
            cc_addresses=[],
        )

        assert result is True
        content = b"".join(written_content).decode("utf-8")
        # Should not have a Subject header when empty
        assert "Subject:" not in content or "Subject: \n" not in content

    @patch("report_generator.output.email_draft.EmailDraftHandler._open_in_browser")
    @patch("tempfile.NamedTemporaryFile")
    def test_eml_draft_falls_back_to_browser_on_exception(
        self, mock_tempfile, mock_browser
    ):
        """Test that EML draft falls back to browser on exception."""
        mock_tempfile.side_effect = Exception("Failed to create temp file")
        mock_browser.return_value = True

        handler = EmailDraftHandler()
        result = handler._open_eml_draft(
            html_content="<h1>Test</h1>",
            subject="Test",
            to_addresses=[],
            cc_addresses=[],
        )

        # Should fall back to browser
        mock_browser.assert_called_once_with("<h1>Test</h1>")

    @patch("report_generator.output.email_draft.EmailDraftHandler._open_in_browser")
    @patch("tempfile.NamedTemporaryFile")
    def test_eml_draft_returns_browser_result_on_exception(
        self, mock_tempfile, mock_browser
    ):
        """Test that EML draft returns browser result when falling back."""
        mock_tempfile.side_effect = Exception("Failed")
        mock_browser.return_value = False  # Browser also fails

        handler = EmailDraftHandler()
        result = handler._open_eml_draft(
            html_content="<h1>Test</h1>",
            subject="Test",
            to_addresses=[],
            cc_addresses=[],
        )

        assert result is False


class TestOpenInBrowser:
    """Tests for the _open_in_browser method."""

    @patch("webbrowser.open")
    @patch("tempfile.NamedTemporaryFile")
    def test_browser_creates_html_file(self, mock_tempfile, mock_browser):
        """Test that browser fallback creates HTML temp file."""
        mock_file = MagicMock()
        mock_file.name = "/tmp/test.html"
        mock_file.__enter__ = MagicMock(return_value=mock_file)
        mock_file.__exit__ = MagicMock(return_value=False)
        mock_tempfile.return_value = mock_file

        handler = EmailDraftHandler()
        result = handler._open_in_browser("<h1>Test Content</h1>")

        assert result is True
        mock_file.write.assert_called_once_with("<h1>Test Content</h1>")

    @patch("webbrowser.open")
    @patch("tempfile.NamedTemporaryFile")
    def test_browser_opens_file_url(self, mock_tempfile, mock_browser):
        """Test that browser is opened with file:// URL."""
        mock_file = MagicMock()
        mock_file.name = "/tmp/report.html"
        mock_file.__enter__ = MagicMock(return_value=mock_file)
        mock_file.__exit__ = MagicMock(return_value=False)
        mock_tempfile.return_value = mock_file

        handler = EmailDraftHandler()
        handler._open_in_browser("<h1>Test</h1>")

        mock_browser.assert_called_once_with("file:///tmp/report.html")

    @patch("webbrowser.open")
    @patch("tempfile.NamedTemporaryFile")
    def test_browser_returns_false_on_exception(self, mock_tempfile, mock_browser):
        """Test that browser returns False on exception."""
        mock_tempfile.side_effect = Exception("Failed to create temp file")

        handler = EmailDraftHandler()
        result = handler._open_in_browser("<h1>Test</h1>")

        assert result is False

    @patch("webbrowser.open")
    @patch("tempfile.NamedTemporaryFile")
    def test_browser_returns_false_on_webbrowser_exception(
        self, mock_tempfile, mock_browser
    ):
        """Test that browser returns False when webbrowser.open fails."""
        mock_file = MagicMock()
        mock_file.name = "/tmp/test.html"
        mock_file.__enter__ = MagicMock(return_value=mock_file)
        mock_file.__exit__ = MagicMock(return_value=False)
        mock_tempfile.return_value = mock_file

        mock_browser.side_effect = Exception("Browser failed to open")

        handler = EmailDraftHandler()
        result = handler._open_in_browser("<h1>Test</h1>")

        assert result is False


class TestIntegration:
    """Integration tests for email draft handler."""

    @patch("subprocess.run")
    def test_full_flow_darwin_success(self, mock_run):
        """Test full flow on darwin with successful result."""
        mock_run.return_value = MagicMock(returncode=0)

        handler = EmailDraftHandler()
        handler.platform = "darwin"

        result = handler.open_draft(
            html_content="<html><body><h1>Weekly Report</h1></body></html>",
            subject="Weekly Status Report - January 2025",
            to_addresses=["team@example.com", "manager@example.com"],
            cc_addresses=["stakeholder@example.com"],
        )

        assert result is True
        assert mock_run.called

        # Verify open command was called
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "open"
        assert call_args[1].endswith(".eml")

    @patch("webbrowser.open")
    def test_full_flow_non_darwin(self, mock_browser):
        """Test full flow on non-darwin platform."""
        handler = EmailDraftHandler()
        handler.platform = "linux"

        result = handler.open_draft(
            html_content="<html><body><h1>Report</h1></body></html>", subject="Report"
        )

        assert result is True
        assert mock_browser.called

        # Verify file:// URL was opened
        call_args = mock_browser.call_args[0][0]
        assert call_args.startswith("file://")
        assert call_args.endswith(".html")
