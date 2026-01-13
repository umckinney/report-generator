"""
Unit tests for risk analysis prompt generation.
"""

from report_generator.reasoning.prompts import risk_analysis


class TestRiskAnalysisPrompt:
    """Tests for risk analysis prompt building."""

    def test_build_prompt_with_risks(self):
        """Test prompt construction with valid risks."""
        context = {
            "status_groups": [
                (
                    "At Risk",
                    [
                        {
                            "deliverable": "Feature A",
                            "risks_issues": "Resource constraints impacting delivery",
                        }
                    ],
                ),
                (
                    "Off Track",
                    [
                        {
                            "deliverable": "Feature B",
                            "risks_issues": "Dependency delays from Team C",
                        }
                    ],
                ),
            ]
        }

        prompt = risk_analysis.build_prompt(context)

        assert prompt is not None
        assert "Feature A" in prompt
        assert "Feature B" in prompt
        assert "Resource constraints" in prompt
        assert "Dependency delays" in prompt
        assert "At Risk" in prompt
        assert "Off Track" in prompt
        assert "Cross-Cutting Themes" in prompt
        assert "JSON" in prompt

    def test_build_prompt_no_risks(self):
        """Test prompt returns None when no risks to analyze."""
        context = {
            "status_groups": [
                (
                    "On Track",
                    [
                        {
                            "deliverable": "Feature A",
                            "risks_issues": "No risks or issues reported this week",
                        }
                    ],
                )
            ]
        }

        prompt = risk_analysis.build_prompt(context)

        assert prompt is None

    def test_build_prompt_empty_status_groups(self):
        """Test prompt returns None for empty status groups."""
        context = {"status_groups": []}

        prompt = risk_analysis.build_prompt(context)

        assert prompt is None

    def test_build_prompt_filters_empty_risks(self):
        """Test that empty/default risks are filtered out."""
        context = {
            "status_groups": [
                (
                    "At Risk",
                    [
                        {"deliverable": "Feature A", "risks_issues": "Real risk here"},
                        {"deliverable": "Feature B", "risks_issues": ""},
                        {"deliverable": "Feature C", "risks_issues": "none"},
                        {"deliverable": "Feature D", "risks_issues": "N/A"},
                    ],
                )
            ]
        }

        prompt = risk_analysis.build_prompt(context)

        assert prompt is not None
        assert "Feature A" in prompt
        assert "Real risk" in prompt
        # Filtered items should not appear
        assert "Feature B" not in prompt
        assert "Feature C" not in prompt
        assert "Feature D" not in prompt

    def test_extract_risks_basic(self):
        """Test basic risk extraction."""
        status_groups = [
            (
                "At Risk",
                [
                    {
                        "deliverable": "Feature X",
                        "risks_issues": "Testing delays",
                    }
                ],
            )
        ]

        risks = risk_analysis._extract_risks(status_groups)

        assert len(risks) == 1
        assert risks[0]["deliverable"] == "Feature X"
        assert risks[0]["status"] == "At Risk"
        assert risks[0]["risk"] == "Testing delays"

    def test_extract_risks_multiple_statuses(self):
        """Test extraction across multiple status groups."""
        status_groups = [
            (
                "At Risk",
                [
                    {"deliverable": "A", "risks_issues": "Risk A"},
                    {"deliverable": "B", "risks_issues": "Risk B"},
                ],
            ),
            (
                "Off Track",
                [
                    {"deliverable": "C", "risks_issues": "Risk C"},
                ],
            ),
            (
                "On Track",
                [
                    {"deliverable": "D", "risks_issues": "Risk D"},
                ],
            ),
        ]

        risks = risk_analysis._extract_risks(status_groups)

        assert len(risks) == 4
        deliverables = [r["deliverable"] for r in risks]
        assert "A" in deliverables
        assert "B" in deliverables
        assert "C" in deliverables
        assert "D" in deliverables

    def test_extract_risks_filters_defaults(self):
        """Test that default risk messages are filtered."""
        status_groups = [
            (
                "At Risk",
                [
                    {"deliverable": "A", "risks_issues": "Real risk"},
                    {
                        "deliverable": "B",
                        "risks_issues": "No risks or issues reported this week",
                    },
                    {"deliverable": "C", "risks_issues": "none"},
                    {"deliverable": "D", "risks_issues": "N/A"},
                    {"deliverable": "E", "risks_issues": ""},
                ],
            )
        ]

        risks = risk_analysis._extract_risks(status_groups)

        assert len(risks) == 1
        assert risks[0]["deliverable"] == "A"

    def test_format_risks(self):
        """Test risk formatting for prompt."""
        risks = [
            {
                "deliverable": "Feature A",
                "status": "At Risk",
                "risk": "Resource constraints",
            },
            {
                "deliverable": "Feature B",
                "status": "Off Track",
                "risk": "Dependency delays",
            },
        ]

        formatted = risk_analysis._format_risks(risks)

        assert "**Feature A** (At Risk)" in formatted
        assert "Risk: Resource constraints" in formatted
        assert "**Feature B** (Off Track)" in formatted
        assert "Risk: Dependency delays" in formatted

    def test_parse_response_valid_json(self):
        """Test parsing valid JSON response."""
        response = """{
            "themes": [
                {
                    "name": "Resource Constraints",
                    "description": "Multiple teams facing staffing issues",
                    "affected_deliverables": ["Feature A", "Feature B"],
                    "severity": "high"
                }
            ],
            "critical_risks": [
                {
                    "deliverable": "Feature A",
                    "risk": "Team understaffed",
                    "reason": "Impacts launch timeline"
                }
            ],
            "anomalies": [
                {
                    "deliverable": "Feature C",
                    "issue": "Marked On Track but has major risks"
                }
            ]
        }"""

        result = risk_analysis.parse_response(response)

        assert "themes" in result
        assert len(result["themes"]) == 1
        assert result["themes"][0]["name"] == "Resource Constraints"
        assert result["themes"][0]["severity"] == "high"

        assert "critical_risks" in result
        assert len(result["critical_risks"]) == 1
        assert result["critical_risks"][0]["deliverable"] == "Feature A"

        assert "anomalies" in result
        assert len(result["anomalies"]) == 1
        assert result["anomalies"][0]["deliverable"] == "Feature C"

    def test_parse_response_missing_fields(self):
        """Test parsing JSON with missing fields."""
        response = '{"themes": []}'

        result = risk_analysis.parse_response(response)

        assert "themes" in result
        assert "critical_risks" in result
        assert "anomalies" in result
        assert result["themes"] == []
        assert result["critical_risks"] == []
        assert result["anomalies"] == []

    def test_parse_response_invalid_json(self):
        """Test handling of malformed JSON."""
        response = "This is not valid JSON"

        result = risk_analysis.parse_response(response)

        assert "themes" in result
        assert "critical_risks" in result
        assert "anomalies" in result
        assert "parse_error" in result
        assert result["themes"] == []
        assert result["critical_risks"] == []
        assert result["anomalies"] == []

    def test_parse_response_empty_arrays(self):
        """Test parsing response with empty arrays."""
        response = """{
            "themes": [],
            "critical_risks": [],
            "anomalies": []
        }"""

        result = risk_analysis.parse_response(response)

        assert result["themes"] == []
        assert result["critical_risks"] == []
        assert result["anomalies"] == []
        assert "parse_error" not in result
