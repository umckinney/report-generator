"""
HTML report generator for Key Priorities report.

This module orchestrates the complete report generation process:
Load → Validate → Transform → Build → Render → Save
"""

import base64
from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader

from report_generator.data.loader import TabularDataLoader
from report_generator.data.transformers import DataTransformer
from report_generator.data.validator import DataValidator
from report_generator.reports.example_report.builder import KPRReportBuilder
from report_generator.reports.example_report.config import (
    EXPECTED_COLUMNS,
    clean_transformed_row,
    get_transformer_config,
)


class KPRReportGenerator:
    """
    Generates KPR HTML reports from CSV data.

    This class orchestrates the full pipeline for generating
    the Key Priorities report.

    Example:
        >>> generator = KPRReportGenerator()
        >>> html = generator.generate("data/kpr.csv")
        >>> # HTML string ready to save or send
    """

    def __init__(self):
        """Initialize the report generator."""
        self.loader = TabularDataLoader()
        self.validator = DataValidator()
        self.builder = KPRReportBuilder()

        # Setup Jinja2 template environment
        template_dir = Path(__file__).parent
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
        self.template = self.jinja_env.get_template("template.html")

        # Load logo as base64 (optional - place your logo in assets/logo.png)
        logo_path = template_dir / "assets" / "logo.png"
        if logo_path.exists():
            with open(logo_path, "rb") as f:
                logo_bytes = f.read()
                self.logo_base64 = base64.b64encode(logo_bytes).decode("utf-8")
        else:
            self.logo_base64 = ""  # No logo if file missing

    def generate(self, csv_path: str | Path, output_path: Optional[str | Path] = None) -> str:
        """
        Generate KPR report from CSV file.

        Full pipeline:
        1. Load CSV data
        2. Validate structure
        3. Transform data
        4. Build template context
        5. Render HTML
        6. Optionally save to file

        Args:
            csv_path: Path to CSV file with KPR data
            output_path: Optional path to save HTML output

        Returns:
            HTML string of rendered report

        Raises:
            FileNotFoundError: If CSV file doesn't exist
            ValueError: If data validation fails catastrophically

        Example:
            >>> generator = KPRReportGenerator()
            >>> html = generator.generate("data/kpr.csv", "output/report.html")
            >>> print(f"Report saved to output/report.html")
        """
        # Step 1: Load data
        print(f"Loading data from {csv_path}...")
        raw_data = self.loader.load(csv_path)
        print(f"✓ Loaded {len(raw_data)} rows")

        # Step 2: Validate structure
        print("Validating data structure...")
        schema = {"expected_columns": EXPECTED_COLUMNS}
        validation_result = self.validator.validate(raw_data, schema)

        if not validation_result["valid"]:
            raise ValueError("Data validation failed:\n" + "\n".join(validation_result["errors"]))

        # Show warnings if any
        if validation_result["warnings"]:
            print("⚠ Warnings:")
            for warning in validation_result["warnings"]:
                print(f"  - {warning}")

        print("✓ Validation passed")

        # Step 3: Transform data
        print("Transforming data...")
        field_mappings, transformations = get_transformer_config()
        transformer = DataTransformer(field_mappings, transformations)
        transformed_data = transformer.transform(raw_data)

        # Clean up (parse leads)
        final_data = [clean_transformed_row(row) for row in transformed_data]
        print(f"✓ Transformed {len(final_data)} deliverables")

        # Step 4: Build template context
        print("Building report context...")
        context = self.builder.build_context(final_data)

        # Add logo
        context["logo_base64"] = self.logo_base64

        print("✓ Context ready")

        # Step 4.5: Apply reasoning layer (if enabled)
        from report_generator.reasoning import get_config

        reasoning_config = get_config()
        if reasoning_config.is_enabled():
            try:
                print("Generating AI insights...")
                provider = reasoning_config.get_provider()
                from report_generator.reasoning import ReportSynthesizer

                synthesizer = ReportSynthesizer(
                    provider,
                    max_tokens=reasoning_config.max_tokens,
                    temperature=reasoning_config.temperature,
                )
                context = synthesizer.synthesize(
                    context, features={"executive_summary": True}
                )
                print(f"✓ AI synthesis complete (tokens: {synthesizer.get_token_usage()})")
            except Exception as e:
                print(f"⚠ Warning: AI synthesis failed: {e}")
                # Continue without synthesis - graceful degradation

        # Step 5: Render template
        print("Rendering HTML template...")
        html = self.template.render(context)
        print("✓ Template rendered")

        # Step 6: Save to file if requested
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(html, encoding="utf-8")
            print(f"✓ Report saved to {output_path}")

        return html

    def generate_from_data(self, data: list[dict]) -> str:
        """
        Generate report from already-loaded data.

        Useful for testing or when data comes from non-CSV source.

        Args:
            data: List of dictionaries (already transformed and cleaned)

        Returns:
            HTML string of rendered report

        Example:
            >>> data = [{"deliverable": "Test", "status": "On Track", ...}]
            >>> html = generator.generate_from_data(data)
        """
        context = self.builder.build_context(data)
        html = self.template.render(context)
        return html
