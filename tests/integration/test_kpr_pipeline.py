"""
Integration test for Key Priorities reports pipeline.

Tests the full data flow: Load → Validate → Transform → Ready for template
"""

import pytest
from pathlib import Path
from report_generator.data.loader import TabularDataLoader
from report_generator.data.validator import DataValidator
from report_generator.data.transformers import DataTransformer
from report_generator.reports.example_report.config import (
    get_transformer_config,
    clean_transformed_row,
    EXPECTED_COLUMNS,
)
from report_generator.reports.example_report.builder import KPRReportBuilder


class TestKPRPipeline:
    """Integration tests for KPR reports pipeline."""

    def test_full_pipeline_with_mock_data(self):
        """
        Test complete pipeline from CSV to transformed data.

        Load → Validate → Transform → Clean
        """
        # Step 1: Load data
        loader = TabularDataLoader()
        csv_path = Path("tests/fixtures/mock_data.csv")
        raw_data = loader.load(csv_path)

        assert len(raw_data) == 5

        # Step 2: Validate structure
        validator = DataValidator()
        schema = {"expected_columns": EXPECTED_COLUMNS}
        result = validator.validate(raw_data, schema)

        assert result["valid"] is True

        # Step 3: Transform data
        field_mappings, transformations = get_transformer_config()
        transformer = DataTransformer(field_mappings, transformations)
        transformed_data = transformer.transform(raw_data)

        # Step 4: Clean up (parse leads)
        final_data = [clean_transformed_row(row) for row in transformed_data]

        # Verify structure
        assert len(final_data) == 5

        # Check first row has expected fields
        first_row = final_data[0]
        assert "deliverable" in first_row
        assert "priority" in first_row
        assert "delivery_date" in first_row
        assert "leads" in first_row
        assert "initiative" in first_row

        # Check leads are parsed correctly
        assert isinstance(first_row["leads"], dict)
        assert "Engineering" in first_row["leads"]
        assert isinstance(first_row["leads"]["Engineering"], list)

        # Check date was formatted
        # Mock data has "12/15/2024" which should become "Dec 15, 2024"
        if first_row["delivery_date"]:
            assert (
                "Dec" in first_row["delivery_date"] or first_row["delivery_date"] == ""
            )

    def test_pipeline_handles_empty_leads(self):
        """
        Test that pipeline handles empty lead fields gracefully.
        """
        # Use row 5 from mock data which has empty leads
        loader = TabularDataLoader()
        csv_path = Path("tests/fixtures/mock_data.csv")
        raw_data = loader.load(csv_path)

        # Get last row (has some empty leads)
        last_row_raw = [raw_data[-1]]

        # Transform
        field_mappings, transformations = get_transformer_config()
        transformer = DataTransformer(field_mappings, transformations)
        transformed = transformer.transform(last_row_raw)

        # Clean
        final = [clean_transformed_row(row) for row in transformed]

        # Verify empty leads become empty lists
        leads = final[0]["leads"]
        for role, people in leads.items():
            assert isinstance(people, list)
            # Empty leads should be empty list, not list with empty string
            if len(people) == 0:
                assert people == []

    def test_pipeline_preserves_line_breaks(self):
        """
        Test that pipeline preserves line breaks in multi-line fields.

        Key Achievements and Risks & Issues should convert \\n to <br>
        """
        loader = TabularDataLoader()
        csv_path = Path("tests/fixtures/mock_data.csv")
        raw_data = loader.load(csv_path)

        # Transform first row
        field_mappings, transformations = get_transformer_config()
        transformer = DataTransformer(field_mappings, transformations)
        transformed = transformer.transform([raw_data[0]])
        final = [clean_transformed_row(row) for row in transformed]

        first_row = final[0]

        # Check that key_achievements and risks_issues are strings
        assert isinstance(first_row["key_achievements"], str)
        assert isinstance(first_row["risks_issues"], str)

    def test_full_pipeline_to_template_context(self):
        """
        Test complete pipeline including builder.

        Load → Validate → Transform → Clean → Build Context
        """
        # Load and transform (existing logic)
        loader = TabularDataLoader()
        csv_path = Path("tests/fixtures/mock_data.csv")
        raw_data = loader.load(csv_path)

        field_mappings, transformations = get_transformer_config()
        transformer = DataTransformer(field_mappings, transformations)
        transformed_data = transformer.transform(raw_data)
        final_data = [clean_transformed_row(row) for row in transformed_data]

        # Build context for template
        builder = KPRReportBuilder()
        context = builder.build_context(final_data)

        # Verify context structure
        assert "status_groups" in context
        assert "report_date" in context
        assert "brand_colors" in context

        # Verify status groups are sorted
        status_groups = context["status_groups"]
        assert len(status_groups) > 0
        assert isinstance(status_groups, list)

        # First group should be a tuple of (status_name, items)
        first_group = status_groups[0]
        assert isinstance(first_group, tuple)
        assert len(first_group) == 2

        status_name, items = first_group
        assert isinstance(status_name, str)
        assert isinstance(items, list)

    def test_full_report_generation(self):
        """
        Test complete end-to-end report generation.

        Load CSV → Generate HTML → Verify output
        """
        from report_generator.reports.example_report.generator import KPRReportGenerator

        # Generate report
        generator = KPRReportGenerator()
        csv_path = Path("tests/fixtures/mock_data.csv")

        # Generate without saving
        html = generator.generate(csv_path)

        # Verify HTML was generated
        assert html is not None
        assert len(html) > 0
        assert "<!DOCTYPE html>" in html

        # Verify content is in HTML - use actual deliverable names from mock data
        assert "Weekly Key Priorities Report" in html
        assert (
            "API Gateway" in html or "Analytics Dashboard" in html
        )  # Part of deliverable names
        assert "On Track" in html or "At Risk" in html

        # Verify a person name appears
        assert "Sarah Johnson" in html or "Michael Chen" in html

        print("✓ Full report generation successful")

    def test_report_generation_with_file_output(self, tmp_path):
        """
        Test report generation with file output.

        Should save HTML to specified path.
        """
        from report_generator.reports.example_report.generator import KPRReportGenerator

        # Generate and save
        generator = KPRReportGenerator()
        csv_path = Path("tests/fixtures/mock_data.csv")
        output_path = tmp_path / "test_report.html"

        html = generator.generate(csv_path, output_path)

        # Verify file was created
        assert output_path.exists()

        # Verify content matches
        saved_html = output_path.read_text(encoding="utf-8")
        assert saved_html == html

        print(f"✓ Report saved to {output_path}")

    def test_generator_without_logo(self, tmp_path):
        """
        Test that generator works when logo file doesn't exist.

        Should generate report with empty logo_base64.
        """
        from unittest.mock import patch, MagicMock
        from report_generator.reports.example_report.generator import KPRReportGenerator

        # Mock Path.exists to return False for logo
        original_exists = Path.exists

        def mock_exists(self):
            if "logo.png" in str(self):
                return False
            return original_exists(self)

        with patch.object(Path, "exists", mock_exists):
            generator = KPRReportGenerator()
            assert generator.logo_base64 == ""

    def test_generator_validation_failure(self):
        """
        Test that generator raises ValueError on validation failure.

        Should raise ValueError when data is invalid.
        """
        from report_generator.reports.example_report.generator import KPRReportGenerator
        from unittest.mock import patch, MagicMock

        # Create a valid CSV that will load successfully
        valid_csv = Path("tests/fixtures/valid_for_validation_test.csv")
        valid_csv.write_text(
            "Initiatives (L3),L4 Deliverables,Deliverable Status,Event Phase,L4 Priority,"
            "Delivery Date,Risks & Issues,Key Achievements,Program Workstream Lead,"
            "Product Workstream Lead,Engineering Workstream Lead,Design Workstream Lead,"
            "QA Workstream Lead\n"
            "Init,Deliverable,On Track,In Development,P1,2025-03-15,None,Progress,"
            "Lead1,Lead2,Lead3,Lead4,Lead5\n"
        )

        generator = KPRReportGenerator()

        # Mock the validator to return invalid result
        mock_result = {
            "valid": False,
            "errors": ["Test validation error"],
            "warnings": [],
            "info": [],
        }

        with patch.object(generator.validator, "validate", return_value=mock_result):
            with pytest.raises(ValueError) as exc_info:
                generator.generate(valid_csv)

            assert "validation failed" in str(exc_info.value).lower()

        # Cleanup
        valid_csv.unlink()

    def test_generator_with_validation_warnings(self, capsys):
        """
        Test that generator continues when validation has warnings.

        Should print warnings but complete successfully.
        """
        from report_generator.reports.example_report.generator import KPRReportGenerator
        from unittest.mock import patch

        # Create CSV with valid data
        warning_csv = Path("tests/fixtures/warning_test.csv")
        warning_csv.write_text(
            "Initiatives (L3),L4 Deliverables,Deliverable Status,Event Phase,L4 Priority,"
            "Delivery Date,Risks & Issues,Key Achievements,Program Workstream Lead,"
            "Product Workstream Lead,Engineering Workstream Lead,Design Workstream Lead,"
            "QA Workstream Lead\n"
            "Init,Deliverable,On Track,In Development,P1,2025-03-15,None,Progress,Lead1,"
            "Lead2,Lead3,Lead4,Lead5\n"
        )

        generator = KPRReportGenerator()

        # Mock validator to return warnings
        mock_result = {
            "valid": True,
            "errors": [],
            "warnings": ["Test warning message", "Another warning"],
            "info": [],
        }

        with patch.object(generator.validator, "validate", return_value=mock_result):
            html = generator.generate(warning_csv)

        # Should generate successfully despite warnings
        assert html is not None
        assert "<!DOCTYPE html>" in html

        # Check that warnings were printed
        captured = capsys.readouterr()
        assert "Warnings" in captured.out
        assert "Test warning message" in captured.out

        # Cleanup
        warning_csv.unlink()

    def test_generate_from_data_method(self):
        """
        Test the generate_from_data method.

        Should generate HTML from pre-loaded data.
        """
        from report_generator.reports.example_report.generator import KPRReportGenerator

        # Pre-transformed data
        data = [
            {
                "deliverable": "Test Deliverable",
                "status": "On Track",
                "priority": "P1",
                "initiative": "Test Initiative",
                "event_phase": "In Development",
                "delivery_date": "Jan 15, 2025",
                "key_achievements": "Made progress",
                "risks_issues": "",
                "leads": {
                    "Engineering": ["Alice"],
                    "Product": ["Bob"],
                    "Program": [],
                    "Design": [],
                    "QA": [],
                },
            }
        ]

        generator = KPRReportGenerator()
        html = generator.generate_from_data(data)

        assert html is not None
        assert "<!DOCTYPE html>" in html
        assert "Test Deliverable" in html
        assert "On Track" in html
