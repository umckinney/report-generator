"""
Unit tests for action items prompt generation.

Tests the prompt building and response parsing for AI-generated action items.
"""

import json

import pytest

from report_generator.reasoning.prompts import action_items


class TestActionItemsPrompt:
    """Tests for action items prompt building."""

    def test_build_prompt_with_critical_deliverables(self):
        """Test prompt generation with critical deliverables."""
        context = {
            "total_deliverables": 3,
            "status_groups": [
                ("Off Track", [{"name": "API"}]),
                ("At Risk", [{"name": "Database"}]),
                ("On Track", [{"name": "Frontend"}]),
            ],
            "deliverables": [
                {
                    "deliverable": "API Upgrade",
                    "status": "Off Track",
                    "lead": "Alice",
                    "risks_issues": "Team understaffed",
                    "next_steps": "Hire 2 engineers",
                },
                {
                    "deliverable": "Database Migration",
                    "status": "At Risk",
                    "lead": "Bob",
                    "risks_issues": "Delayed by 2 weeks",
                    "next_steps": "Expedite vendor approval",
                },
                {
                    "deliverable": "Frontend Redesign",
                    "status": "On Track",
                    "lead": "Carol",
                    "risks_issues": "None",
                    "next_steps": "Continue development",
                },
            ],
        }

        prompt = action_items.build_prompt(context)

        assert prompt is not None
        assert "API Upgrade" in prompt
        assert "Database Migration" in prompt
        assert "Frontend Redesign" not in prompt  # On Track items excluded
        assert "Team understaffed" in prompt
        assert "Delayed by 2 weeks" in prompt
        assert "JSON" in prompt  # Should include output format

    def test_build_prompt_with_no_critical_items(self):
        """Test that no prompt is generated when all items are on track."""
        context = {
            "total_deliverables": 2,
            "status_groups": [
                ("On Track", [{"name": "Frontend"}, {"name": "Backend"}]),
            ],
            "deliverables": [
                {
                    "deliverable": "Frontend",
                    "status": "On Track",
                    "lead": "Alice",
                    "risks_issues": "None",
                },
                {
                    "deliverable": "Backend",
                    "status": "On Track",
                    "lead": "Bob",
                    "risks_issues": "None",
                },
            ],
        }

        prompt = action_items.build_prompt(context)

        assert prompt is None  # No actions needed

    def test_build_prompt_with_empty_deliverables(self):
        """Test prompt generation with empty deliverables list."""
        context = {
            "total_deliverables": 0,
            "status_groups": [],
            "deliverables": [],
        }

        prompt = action_items.build_prompt(context)

        assert prompt is None  # No actions needed

    def test_build_prompt_includes_confidence_instructions(self):
        """Test that prompt includes confidence level instructions."""
        context = {
            "total_deliverables": 1,
            "deliverables": [
                {
                    "deliverable": "API",
                    "status": "Off Track",
                    "lead": "Alice",
                    "risks_issues": "Issue",
                    "next_steps": "Fix",
                },
            ],
        }

        prompt = action_items.build_prompt(context)

        assert "confidence" in prompt.lower()
        assert "high" in prompt
        assert "medium" in prompt
        assert "low" in prompt


class TestActionItemsResponseParsing:
    """Tests for action items response parsing."""

    def test_parse_valid_response(self):
        """Test parsing valid JSON response."""
        response = json.dumps(
            {
                "actions": [
                    {
                        "title": "Hire additional engineers for API team",
                        "description": "Prioritize hiring 2 senior engineers to address understaffing",
                        "owner": "Alice",
                        "success_criterion": "Team at full capacity within 30 days",
                        "confidence": "high",
                        "related_deliverables": ["API Upgrade"],
                    },
                    {
                        "title": "Expedite vendor approval process",
                        "description": "Work with procurement to fast-track database vendor selection",
                        "owner": "Bob",
                        "success_criterion": "Vendor approved within 1 week",
                        "confidence": "medium",
                        "related_deliverables": ["Database Migration"],
                    },
                ]
            }
        )

        result = action_items.parse_response(response)

        assert "actions" in result
        assert "count" in result
        assert result["count"] == 2
        assert len(result["actions"]) == 2
        assert result["actions"][0]["title"] == "Hire additional engineers for API team"
        assert result["actions"][0]["confidence"] == "high"
        assert result["actions"][1]["confidence"] == "medium"

    def test_parse_response_with_markdown_fences(self):
        """Test parsing response wrapped in markdown code fences."""
        response = """```json
{
  "actions": [
    {
      "title": "Test action",
      "description": "Test description",
      "owner": "Test Owner",
      "success_criterion": "Test criterion",
      "confidence": "high",
      "related_deliverables": ["Test"]
    }
  ]
}
```"""

        result = action_items.parse_response(response)

        assert result["count"] == 1
        assert result["actions"][0]["title"] == "Test action"

    def test_parse_response_missing_actions_field(self):
        """Test error handling when actions field is missing."""
        response = json.dumps({"results": []})

        with pytest.raises(ValueError, match="missing 'actions' field"):
            action_items.parse_response(response)

    def test_parse_response_actions_not_list(self):
        """Test error handling when actions is not a list."""
        response = json.dumps({"actions": "not a list"})

        with pytest.raises(ValueError, match="'actions' must be a list"):
            action_items.parse_response(response)

    def test_parse_response_missing_required_fields(self):
        """Test error handling when action is missing required fields."""
        response = json.dumps(
            {
                "actions": [
                    {
                        "title": "Test",
                        "description": "Test",
                        # Missing: owner, success_criterion, confidence
                    }
                ]
            }
        )

        with pytest.raises(ValueError, match="missing required field"):
            action_items.parse_response(response)

    def test_parse_response_invalid_confidence(self):
        """Test error handling for invalid confidence level."""
        response = json.dumps(
            {
                "actions": [
                    {
                        "title": "Test",
                        "description": "Test",
                        "owner": "Test",
                        "success_criterion": "Test",
                        "confidence": "super-high",  # Invalid
                        "related_deliverables": [],
                    }
                ]
            }
        )

        with pytest.raises(ValueError, match="invalid confidence"):
            action_items.parse_response(response)

    def test_parse_response_invalid_json(self):
        """Test error handling for invalid JSON."""
        response = "This is not JSON"

        with pytest.raises(ValueError, match="Invalid JSON"):
            action_items.parse_response(response)

    def test_parse_response_with_optional_fields(self):
        """Test that related_deliverables is optional."""
        response = json.dumps(
            {
                "actions": [
                    {
                        "title": "Test action",
                        "description": "Test description",
                        "owner": "Test Owner",
                        "success_criterion": "Test criterion",
                        "confidence": "low",
                        # related_deliverables is optional
                    }
                ]
            }
        )

        result = action_items.parse_response(response)

        assert result["count"] == 1
        # Should not raise error even without related_deliverables
