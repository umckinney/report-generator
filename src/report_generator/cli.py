"""
Command-line interface for report generator.

Provides simple commands for generating reports.
"""

import argparse
import sys
from argparse import Namespace
from datetime import datetime
from pathlib import Path

from report_generator.output.email_draft import EmailDraftHandler
from report_generator.reports.example_report.config import EMAIL_CONFIG as KPR_EMAIL_CONFIG

# Import report generators
from report_generator.reports.example_report.generator import KPRReportGenerator

# Registry of available reports
REPORT_REGISTRY = {
    "kpr": {
        "name": "Key Priorities Report",
        "generator_class": KPRReportGenerator,
        "email_config": KPR_EMAIL_CONFIG,
    },
    # Future reports can be added here:
    # "other-report": {
    #     "name": "Other Report Name",
    #     "generator_class": OtherReportGenerator,
    #     "email_config": OTHER_EMAIL_CONFIG,
    # },
}


def _open_email_draft(html, output_path, report_config):
    """Open email draft with generated report."""
    print("Opening email draft...")
    handler = EmailDraftHandler()
    today = datetime.now().strftime("%B %d, %Y")
    email_config = report_config["email_config"]

    success = handler.open_draft(
        html_content=html,
        subject=email_config["subject"].format(date=today),
        to_addresses=email_config["to"],
        cc_addresses=email_config["cc"],
    )

    if success:
        print("✓ Email draft opened")
    else:
        print("⚠ Could not open email draft")
        print(f"  HTML saved to: {output_path}")
    print()


def _print_error_message(error):
    """Print formatted error message."""
    print()
    print("=" * 70)
    print("✗ ERROR GENERATING REPORT")
    print("=" * 70)
    print(f"Error: {error}")
    print()
    print("Please check:")
    print("  - CSV file is valid and not corrupted")
    print("  - CSV has expected columns")
    print("  - You have write permissions for output directory")
    print()


def generate_report(args):
    """
    Generate a report from CSV.

    Args:
        args: Parsed command-line arguments with report_type, csv, output, email
    """
    report_type = args.report_type

    # Get report configuration
    if report_type not in REPORT_REGISTRY:
        print(f"✗ Error: Unknown report type: {report_type}")
        print(f"Available reports: {', '.join(REPORT_REGISTRY.keys())}")
        return 1

    report_config = REPORT_REGISTRY[report_type]

    print("=" * 70)
    print(f"{report_config['name'].upper()}")
    print("=" * 70)
    print()

    # Validate CSV file exists
    csv_path = Path(args.csv)
    if not csv_path.exists():
        print(f"✗ Error: CSV file not found: {csv_path}")
        print()
        return 1

    # Generate report
    try:
        # Instantiate the appropriate generator
        generator_class = report_config["generator_class"]
        generator = generator_class()

        # Determine output path
        if args.output:
            output_path = Path(args.output)
        else:
            # Default: outputs/{report_type}_report_YYYY-MM-DD.html
            timestamp = datetime.now().strftime("%Y-%m-%d")
            output_path = Path("outputs") / f"{report_type}_report_{timestamp}.html"

        # Generate HTML
        print(f"Generating report from: {csv_path}")
        audience = getattr(args, "audience", None)
        html = generator.generate(csv_path, output_path, audience=audience)

        print()
        print("=" * 70)
        print("✓ REPORT GENERATED SUCCESSFULLY")
        print("=" * 70)
        print(f"Output: {output_path}")
        print(f"Size: {len(html):,} characters")
        print()

        # Open email draft if requested
        if args.email:
            _open_email_draft(html, output_path, report_config)

        return 0

    except Exception as e:  # pylint: disable=broad-exception-caught
        _print_error_message(e)
        return 1


def interactive_mode():
    """Interactive mode - just asks for CSV, always opens email."""
    print("=" * 70)
    print("KPR REPORT GENERATOR")
    print("=" * 70)
    print()
    print("Drag and drop your Airtable CSV file here, then press Enter:")
    print()

    csv_path = input("CSV file: ").strip().strip('"').strip("'")

    if not csv_path:
        print("\n✗ No file provided.")
        input("Press Enter to close...")
        return 1

    args = Namespace(report_type="kpr", csv=csv_path, output=None, email=True)  # Always open email

    result = generate_report(args)

    print()
    input("Press Enter to close...")
    return result


def main():
    """Main CLI entry point."""
    # If no arguments provided, run interactive mode
    # (happens when double-clicking the app)
    if len(sys.argv) == 1:
        return interactive_mode()

    # Otherwise, use normal CLI parsing
    parser = argparse.ArgumentParser(
        description="Generate reports from CSV or TSV",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate KPR report (saves to outputs/)
  python -m report_generator generate --report kpr --csv data.csv

  # Generate executive summary view
  python -m report_generator generate --report kpr --csv data.csv --audience executive

  # Generate partner-safe view
  python -m report_generator generate --report kpr --csv data.csv --audience partner

  # Generate and open email draft
  python -m report_generator generate --report kpr --csv data.csv --email

  # Generate technical view with email
  python -m report_generator generate --report kpr --csv data.csv --audience technical --email

  # List available reports
  python -m report_generator list-reports
        """,
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Generate report command
    generate_parser = subparsers.add_parser("generate", help="Generate a report from CSV or TSV")
    generate_parser.add_argument(
        "--report",
        dest="report_type",
        required=True,
        choices=list(REPORT_REGISTRY.keys()),
        help="Type of report to generate",
    )
    generate_parser.add_argument("--csv", required=True, help="Path to CSV or TSV export file")
    generate_parser.add_argument(
        "--output",
        help="Path for output HTML file (default: outputs/{report}_report_YYYY-MM-DD.html)",
    )
    generate_parser.add_argument(
        "--email",
        action="store_true",
        help="Open email draft in mail client after generating",
    )
    generate_parser.add_argument(
        "--audience",
        choices=["executive", "technical", "partner"],
        help="Target audience for the report (executive: high-level summary, technical: full details, partner: external-safe)",
    )

    # List reports command
    subparsers.add_parser("list-reports", help="List available report types")

    # Parse arguments
    args = parser.parse_args()

    # Execute command
    if args.command == "generate":
        return generate_report(args)
    if args.command == "list-reports":
        print("Available Reports:")
        print("=" * 70)
        for report_id, config in REPORT_REGISTRY.items():
            print(f"  {report_id:20} - {config['name']}")
        print()
        return 0
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
