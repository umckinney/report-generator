"""
Risk analysis prompt template.

This module generates prompts for analyzing risks and extracting themes
across deliverables in a program status report.
"""

from typing import Any, Dict, List, Tuple


def build_prompt(context: Dict[str, Any]) -> str:
    """
    Build risk analysis prompt from report context.

    The prompt asks the LLM to analyze all reported risks and issues,
    identify cross-cutting themes, and flag anomalies.

    Args:
        context: Report context with status_groups, deliverables, etc.

    Returns:
        Formatted prompt string ready for LLM
    """
    status_groups = context.get("status_groups", [])

    # Extract all risks
    risks_by_deliverable = _extract_risks(status_groups)

    if not risks_by_deliverable:
        # No risks to analyze
        return None

    risks_text = _format_risks(risks_by_deliverable)

    prompt = f"""You are analyzing risks and issues from a weekly program status report.

## All Reported Risks and Issues

{risks_text}

## Task

Analyze these risks and provide:

1. **Cross-Cutting Themes** (2-4 themes max)
   - Identify patterns that appear across multiple deliverables
   - Examples: "resource constraints", "dependency delays", "unclear requirements"
   - Only report themes that appear in 2+ deliverables

2. **Severity Assessment**
   - Which risks are most critical?
   - Which require immediate action?

3. **Anomalies** (if any)
   - Deliverables with vague/unclear risk descriptions
   - Risks that seem mismatched with status (e.g., "On Track" with major risks)
   - Missing risk information where expected

## Output Format

Return ONLY valid JSON with this structure:
{{
  "themes": [
    {{
      "name": "Theme name (2-4 words)",
      "description": "Brief explanation (1 sentence)",
      "affected_deliverables": ["Deliverable 1", "Deliverable 2"],
      "severity": "high|medium|low"
    }}
  ],
  "critical_risks": [
    {{
      "deliverable": "Deliverable name",
      "risk": "Risk description",
      "reason": "Why this is critical"
    }}
  ],
  "anomalies": [
    {{
      "deliverable": "Deliverable name",
      "issue": "Description of anomaly"
    }}
  ]
}}

If no themes/anomalies found, use empty arrays. Be concise and specific."""

    return prompt


def _extract_risks(status_groups: List[Tuple[str, List[Dict]]]) -> List[Dict[str, str]]:
    """
    Extract all risks from status groups.

    Args:
        status_groups: List of (status_name, items) tuples

    Returns:
        List of dicts with deliverable and risk text
    """
    risks = []

    for status, items in status_groups:
        for item in items:
            deliverable = item.get("deliverable", "Unknown")
            risk_text = item.get("risks_issues", "").strip()

            # Skip empty or default risks
            if risk_text and risk_text.lower() not in [
                "no risks or issues reported this week",
                "none",
                "n/a",
                "",
            ]:
                risks.append({
                    "deliverable": deliverable,
                    "status": status,
                    "risk": risk_text
                })

    return risks


def _format_risks(risks: List[Dict[str, str]]) -> str:
    """Format risks for prompt."""
    lines = []
    for r in risks:
        lines.append(f"**{r['deliverable']}** ({r['status']})")
        lines.append(f"Risk: {r['risk']}")
        lines.append("")

    return "\n".join(lines)


def parse_response(response: str) -> Dict[str, Any]:
    """
    Parse LLM response into structured format.

    Args:
        response: Raw JSON text from LLM

    Returns:
        Dictionary with parsed risk analysis

    Example:
        >>> response = '{"themes": [...], "critical_risks": [...]}'
        >>> parsed = parse_response(response)
        >>> parsed["themes"]
        [{"name": "Resource Constraints", ...}]
    """
    import json

    try:
        # Parse JSON
        data = json.loads(response.strip())

        # Validate structure
        if "themes" not in data:
            data["themes"] = []
        if "critical_risks" not in data:
            data["critical_risks"] = []
        if "anomalies" not in data:
            data["anomalies"] = []

        return data

    except json.JSONDecodeError as e:
        # Fallback for malformed JSON
        return {
            "themes": [],
            "critical_risks": [],
            "anomalies": [],
            "parse_error": str(e)
        }
