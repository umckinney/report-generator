"""
Unit tests for executive summary prompt generation.
"""

from report_generator.reasoning.prompts import executive_summary


class TestExecutiveSummaryPrompt:
    """Tests for executive summary prompt building."""

    def test_build_prompt_basic(self):
        """Test basic prompt construction."""
        context = {
            "total_deliverables": 10,
            "status_groups": [
                ("On Track", [{"deliverable": "Feature A"}]),
                ("At Risk", [{"deliverable": "Feature B"}]),
            ],
            "report_date": "January 12, 2026",
        }

        prompt = executive_summary.build_prompt(context)

        # Verify key elements are present
        assert "January 12, 2026" in prompt
        assert "10" in prompt  # Total deliverables
        assert "On Track" in prompt
        assert "At Risk" in prompt
        assert "executive summary" in prompt.lower()

    def test_build_prompt_with_risks(self):
        """Test prompt includes risk information."""
        context = {
            "total_deliverables": 5,
            "status_groups": [
                (
                    "Off Track",
                    [
                        {
                            "deliverable": "Critical Feature",
                            "priority": "P0",
                            "risks_issues": "Resource shortage impacting delivery",
                        }
                    ],
                )
            ],
            "report_date": "Test Date",
        }

        prompt = executive_summary.build_prompt(context)

        assert "Critical Feature" in prompt
        assert "Resource shortage" in prompt
        assert "P0" in prompt

    def test_build_prompt_no_deliverables(self):
        """Test prompt handles empty status groups."""
        context = {"total_deliverables": 0, "status_groups": [], "report_date": "Test"}

        prompt = executive_summary.build_prompt(context)

        assert "0" in prompt
        assert prompt is not None
        # Should still have structure
        assert "executive summary" in prompt.lower()

    def test_parse_response_clean(self):
        """Test parsing clean LLM response."""
        response = "Program is on track with 2 at-risk items requiring attention."

        result = executive_summary.parse_response(response)

        assert result["summary"] == response
        assert result["length"] == len(response)
        assert result["sentence_count"] == 1

    def test_parse_response_with_preamble(self):
        """Test parsing response with common preambles."""
        response = "Executive Summary: Program is healthy overall."

        result = executive_summary.parse_response(response)

        # Preamble should be removed
        assert result["summary"] == "Program is healthy overall."
        assert "Executive Summary:" not in result["summary"]

    def test_parse_response_multiple_sentences(self):
        """Test sentence counting."""
        response = (
            "Program is on track. Two items are at risk. " "Immediate action needed on Feature X."
        )

        result = executive_summary.parse_response(response)

        assert result["sentence_count"] == 3
        assert result["length"] > 0

    def test_format_status_breakdown(self):
        """Test status breakdown formatting."""
        status_groups = [
            ("On Track", [{"d": "1"}, {"d": "2"}]),
            ("At Risk", [{"d": "3"}]),
        ]

        result = executive_summary._format_status_breakdown(status_groups)

        assert "On Track: 2 deliverables" in result
        assert "At Risk: 1 deliverable" in result  # Singular

    def test_format_status_breakdown_empty(self):
        """Test handling of empty status groups."""
        result = executive_summary._format_status_breakdown([])

        assert "No" in result or "available" in result

    def test_extract_critical_items(self):
        """Test critical items extraction."""
        status_groups = [
            (
                "Off Track",
                [
                    {
                        "deliverable": "Feature X",
                        "priority": "P0",
                        "risks_issues": "Major blocker",
                    }
                ],
            ),
            (
                "At Risk",
                [
                    {
                        "deliverable": "Feature Y",
                        "priority": "P1",
                        "risks_issues": "Resource constraints",
                    }
                ],
            ),
            ("On Track", [{"deliverable": "Feature Z"}]),
        ]

        result = executive_summary._extract_critical_items(status_groups)

        assert "Feature X" in result
        assert "Feature Y" in result
        assert "Feature Z" not in result  # On Track not included
        assert "P0" in result
        assert "Major blocker" in result

    def test_extract_critical_items_none(self):
        """Test extraction when no critical items."""
        status_groups = [
            ("On Track", [{"deliverable": "A"}]),
            ("Complete", [{"deliverable": "B"}]),
        ]

        result = executive_summary._extract_critical_items(status_groups)

        assert "No critical items" in result or "all deliverables on track" in result

    def test_extract_risks_summary(self):
        """Test risks summary extraction."""
        status_groups = [
            (
                "At Risk",
                [
                    {
                        "deliverable": "Feature A",
                        "risks_issues": "Dependency on Team B",
                    }
                ],
            ),
            (
                "Off Track",
                [
                    {
                        "deliverable": "Feature B",
                        "risks_issues": "No risks or issues reported this week",
                    }
                ],
            ),
        ]

        result = executive_summary._extract_risks_summary(status_groups)

        assert "Feature A" in result
        assert "Dependency on Team B" in result
        # Empty/default risks should be filtered
        assert "Feature B" not in result

    def test_extract_risks_summary_none(self):
        """Test risks extraction when none reported."""
        status_groups = [
            (
                "On Track",
                [{"deliverable": "A", "risks_issues": "No risks or issues reported this week"}],
            )
        ]

        result = executive_summary._extract_risks_summary(status_groups)

        assert "No risks" in result or "not reported" in result.lower()
