"""
Action item generation prompt for Chief of Staff Agent.

This module generates AI-powered action item recommendations based on
program status, risks, and blockers.
"""

import json
from typing import Any, Dict, List, Optional


def build_prompt(context: Dict[str, Any]) -> Optional[str]:
    """
    Build action item generation prompt from context.

    Analyzes deliverables with critical statuses (Off Track, At Risk)
    and generates recommended next steps.

    Args:
        context: Report context with deliverables and status information

    Returns:
        Formatted prompt string, or None if no actionable items
    """
    # Extract critical deliverables (Off Track, At Risk)
    critical_deliverables = []

    if "deliverables" in context:
        for deliverable in context["deliverables"]:
            status = deliverable.get("status", "")
            if status in ["Off Track", "At Risk"]:
                critical_deliverables.append(
                    {
                        "name": deliverable.get("deliverable", "Unknown"),
                        "status": status,
                        "lead": deliverable.get("lead", "Unassigned"),
                        "risks_issues": deliverable.get("risks_issues", "None"),
                        "next_steps": deliverable.get("next_steps", "None"),
                    }
                )

    # If no critical items, no actions needed
    if not critical_deliverables:
        return None

    # Build prompt
    prompt_parts = [
        "You are an AI Chief of Staff helping a program manager identify concrete next steps.",
        "",
        "## Program Status Overview",
        f"Total deliverables: {context.get('total_deliverables', 'Unknown')}",
    ]

    # Add status breakdown
    if "status_groups" in context:
        prompt_parts.append("\nStatus breakdown:")
        for status, items in context["status_groups"]:
            prompt_parts.append(f"  - {status}: {len(items)} items")

    # Add critical deliverables
    prompt_parts.extend(
        [
            "",
            "## Critical Deliverables Requiring Attention",
            "",
        ]
    )

    for idx, item in enumerate(critical_deliverables, 1):
        prompt_parts.extend(
            [
                f"### {idx}. {item['name']} ({item['status']})",
                f"**Lead:** {item['lead']}",
                f"**Risks/Issues:** {item['risks_issues']}",
                f"**Planned Next Steps:** {item['next_steps']}",
                "",
            ]
        )

    # Add task instructions
    prompt_parts.extend(
        [
            "## Task",
            "",
            "Generate 3-5 concrete, actionable recommendations for the program manager.",
            "Each action should:",
            "1. Be specific and implementable (not vague like 'monitor situation')",
            "2. Include who should do it (use existing leads or suggest 'Program Manager')",
            "3. Address the most critical risks/blockers",
            "4. Have a clear success criterion",
            "",
            "Also assign a confidence level (high/medium/low) based on:",
            "- **High**: Action is clearly needed and has obvious next steps",
            "- **Medium**: Action is likely helpful but may need refinement",
            "- **Low**: Action is speculative or requires more investigation",
            "",
            "## Output Format",
            "",
            "Return ONLY valid JSON with this structure:",
            "```json",
            "{",
            '  "actions": [',
            "    {",
            '      "title": "Short action title (5-10 words)",',
            '      "description": "Detailed description of what needs to be done",',
            '      "owner": "Who should do this (lead name or role)",',
            '      "success_criterion": "How to know when this is complete",',
            '      "confidence": "high|medium|low",',
            '      "related_deliverables": ["Deliverable Name 1", "Deliverable Name 2"]',
            "    }",
            "  ]",
            "}",
            "```",
            "",
            "Focus on the highest-impact actions first.",
        ]
    )

    return "\n".join(prompt_parts)


def parse_response(response: str) -> Dict[str, Any]:
    """
    Parse LLM response into structured action items.

    Expects JSON format with action items list.

    Args:
        response: Raw LLM response text

    Returns:
        Dictionary with parsed action items

    Raises:
        ValueError: If response is not valid JSON or missing required fields
    """
    # Clean up response - extract JSON if wrapped in markdown
    response = response.strip()

    # Remove markdown code fences if present
    if response.startswith("```"):
        lines = response.split("\n")
        # Remove first line (```json or ```)
        lines = lines[1:]
        # Remove last line if it's ```
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        response = "\n".join(lines)

    try:
        data = json.loads(response)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in action items response: {e}")

    # Validate structure
    if "actions" not in data:
        raise ValueError("Response missing 'actions' field")

    if not isinstance(data["actions"], list):
        raise ValueError("'actions' must be a list")

    # Validate each action
    required_fields = ["title", "description", "owner", "success_criterion", "confidence"]
    for idx, action in enumerate(data["actions"]):
        for field in required_fields:
            if field not in action:
                raise ValueError(f"Action {idx} missing required field: {field}")

        # Validate confidence level
        if action["confidence"] not in ["high", "medium", "low"]:
            raise ValueError(f"Action {idx} has invalid confidence: {action['confidence']}")

    return {
        "actions": data["actions"],
        "count": len(data["actions"]),
    }
