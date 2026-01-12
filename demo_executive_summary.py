#!/usr/bin/env python3
"""
Demo script for Chief of Staff Agent - Executive Summary Feature

This script demonstrates the AI-powered executive summary generation
using the reasoning layer with real API calls.

Usage:
    export ANTHROPIC_API_KEY="your-key-here"
    python demo_executive_summary.py

Requirements:
    - Anthropic API key set in environment
    - Test CSV data (uses existing fixture)
"""

import os
import sys
from pathlib import Path

# Add src to path for local development
sys.path.insert(0, str(Path(__file__).parent / "src"))


def main():
    """Run the executive summary demo."""
    print("=" * 70)
    print("Chief of Staff Agent - Executive Summary Demo")
    print("=" * 70)
    print()

    # Check for API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ Error: ANTHROPIC_API_KEY environment variable not set")
        print()
        print("Please set your API key:")
        print('  export ANTHROPIC_API_KEY="your-key-here"')
        print()
        return 1

    # Enable reasoning
    os.environ["ENABLE_REASONING"] = "true"

    print("✓ API key found")
    print("✓ Reasoning layer enabled")
    print()

    # Find test CSV
    test_csv = Path(__file__).parent / "tests" / "fixtures" / "KeyPrioritiesReview-10.csv"
    if not test_csv.exists():
        print(f"❌ Error: Test CSV not found at {test_csv}")
        return 1

    print(f"✓ Test data found: {test_csv.name}")
    print()

    # Generate report with AI synthesis
    print("-" * 70)
    print("Generating Report with AI Executive Summary...")
    print("-" * 70)
    print()

    try:
        from report_generator.reports.example_report.generator import (
            KPRReportGenerator,
        )

        generator = KPRReportGenerator()

        # Generate with AI insights
        output_path = Path("outputs") / "demo_with_ai_summary.html"
        html = generator.generate(test_csv, output_path=output_path)

        print()
        print("=" * 70)
        print("✓ Report Generated Successfully!")
        print("=" * 70)
        print()
        print(f"📄 Report saved to: {output_path}")
        print(f"📏 Report size: {len(html):,} characters")
        print()

        # Extract and display the executive summary
        from report_generator.reasoning import get_config

        config = get_config()
        if config.is_enabled():
            print("-" * 70)
            print("AI-Generated Executive Summary")
            print("-" * 70)
            print()

            # Find synthesis in the context (it's embedded in the generator)
            # For demo purposes, we'll regenerate just the synthesis part
            from report_generator.data.loader import TabularDataLoader
            from report_generator.data.transformers import DataTransformer
            from report_generator.reports.example_report.builder import (
                KPRReportBuilder,
            )
            from report_generator.reports.example_report.config import (
                EXPECTED_COLUMNS,
                clean_transformed_row,
                get_transformer_config,
            )
            from report_generator.reasoning import ReportSynthesizer

            # Quick re-processing to show summary (simplified)
            loader = TabularDataLoader()
            raw_data = loader.load(test_csv)

            field_mappings, transformations = get_transformer_config()
            transformer = DataTransformer(field_mappings, transformations)
            transformed_data = transformer.transform(raw_data)
            final_data = [clean_transformed_row(row) for row in transformed_data]

            builder = KPRReportBuilder()
            context = builder.build_context(final_data)

            provider = config.get_provider()
            synthesizer = ReportSynthesizer(
                provider,
                max_tokens=config.max_tokens,
                temperature=config.temperature,
            )
            enriched = synthesizer.synthesize(
                context, features={"executive_summary": True}
            )

            if "synthesis" in enriched and enriched["synthesis"].get(
                "executive_summary"
            ):
                summary = enriched["synthesis"]["executive_summary"]
                model = enriched["synthesis"].get("model", "unknown")
                generated_at = enriched["synthesis"].get("generated_at", "unknown")

                print(f'"{summary}"')
                print()
                print(f"Model: {model}")
                print(f"Generated: {generated_at}")
                print()

                # Token usage
                usage = synthesizer.get_token_usage()
                print(f"Token Usage:")
                print(f"  Input:  {usage['input_tokens']:,} tokens")
                print(f"  Output: {usage['output_tokens']:,} tokens")
                print(
                    f"  Total:  {usage['input_tokens'] + usage['output_tokens']:,} tokens"
                )
                print()

        print("-" * 70)
        print("Next Steps:")
        print("-" * 70)
        print()
        print(f"1. Open the report: open {output_path}")
        print("2. Look for the 'Executive Summary' section at the top")
        print("3. Note the 'AI-Generated' badge")
        print("4. Compare with/without reasoning enabled")
        print()
        print("To disable AI features:")
        print("  unset ENABLE_REASONING")
        print()

        return 0

    except Exception as e:
        print()
        print("=" * 70)
        print("❌ Error generating report")
        print("=" * 70)
        print()
        print(f"Error: {e}")
        print()
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
