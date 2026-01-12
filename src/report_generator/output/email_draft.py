"""
Email draft handler for opening reports in mail clients.

This module handles opening HTML reports as email drafts in the user's
default mail client (Mac Mail, Outlook, etc.).
"""

import subprocess
import sys
import tempfile
import webbrowser
from email import policy
from email.message import EmailMessage
from typing import Optional


class EmailDraftHandler:  # pylint: disable=too-few-public-methods
    """
    Opens HTML reports as email drafts in mail client.

    On macOS, writes a .eml file and asks the OS to open it with the
    default mail client (typically Mail, but Outlook etc. will work too).
    On other platforms, falls back to opening HTML in the browser.

    Example:
        >>> handler = EmailDraftHandler()
        >>> handler.open_draft(
        ...     html_content="<html>...</html>",
        ...     subject="Weekly Report",
        ...     to_addresses=["team@example.com"]
        ... )
    """

    def __init__(self):
        """Initialize the email draft handler."""
        self.platform = sys.platform

    def open_draft(
        self,
        html_content: str,
        subject: str = "",
        to_addresses: Optional[list[str]] = None,
        cc_addresses: Optional[list[str]] = None,
    ) -> bool:
        """
        Open HTML content as an email draft in the mail client.

        On macOS, creates a .eml file with HTML content and opens it
        with the default mail client. On other platforms, saves HTML
        and opens it in the browser.

        Args:
            html_content: HTML string to use as email body.
            subject: Email subject line.
            to_addresses: List of recipient email addresses.
            cc_addresses: List of CC email addresses.

        Returns:
            True if successful, False otherwise.
        """
        to_addresses = to_addresses or []
        cc_addresses = cc_addresses or []

        if self.platform == "darwin":
            # Use .eml draft approach on macOS
            return self._open_eml_draft(html_content, subject, to_addresses, cc_addresses)
        # Fallback: save HTML and open in browser
        print(f"⚠ Email draft not supported on {self.platform}")
        print("Opening HTML in browser instead...")
        return self._open_in_browser(html_content)

    def _open_eml_draft(
        self,
        html_content: str,
        subject: str,
        to_addresses: list[str],
        cc_addresses: list[str],
    ) -> bool:
        """
        Create an .eml file containing the HTML body and open it.

        This avoids relying on AppleScript's 'html content' support,
        which is unreliable in modern macOS Mail.
        """
        try:
            # Build email message with HTML + plain-text fallback
            msg = EmailMessage(policy=policy.default)

            if subject:
                msg["Subject"] = subject
            if to_addresses:
                msg["To"] = ", ".join(to_addresses)
            if cc_addresses:
                msg["Cc"] = ", ".join(cc_addresses)

            # Plain-text fallback (if HTML isn't rendered for some reason)
            msg.set_content(
                "This message includes an HTML report. "
                "If you are seeing this text, your mail client "
                "may not be rendering the HTML portion."
            )

            # HTML alternative body
            msg.add_alternative(html_content, subtype="html")

            # Save as temporary .eml file
            with tempfile.NamedTemporaryFile(mode="wb", suffix=".eml", delete=False) as f:
                f.write(msg.as_bytes())
                temp_path = f.name

            # Ask macOS to open the .eml with the default mail client
            # (Mail, Outlook, etc.)
            subprocess.run(["open", temp_path], check=False)

            print(f"✓ EML draft opened: {temp_path}")
            return True

        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"✗ Failed to open EML draft: {e}")
            # Fallback: open HTML in browser so the user can still see the report
            return self._open_in_browser(html_content)

    def _open_in_browser(self, html_content: str) -> bool:
        """
        Fallback: Save HTML to temp file and open in browser.

        Used when mail client integration isn't available.
        """
        try:
            # Create temp file
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".html",
                delete=False,
                encoding="utf-8",
            ) as f:
                f.write(html_content)
                temp_path = f.name

            # Open in browser
            webbrowser.open(f"file://{temp_path}")
            print(f"✓ HTML opened in browser: {temp_path}")
            return True

        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"✗ Failed to open in browser: {e}")
            return False
