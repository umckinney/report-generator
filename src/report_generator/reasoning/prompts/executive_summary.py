"""
Executive summary prompt template.

This module generates prompts for creating concise executive summaries
of program status reports.
"""

from typing import Any, Dict, List, Tuple


def build_prompt(context: Dict[str, Any]) -> str:
    """
    Build executive summary prompt from report context.

    The prompt asks the LLM to generate a 2-3 sentence executive summary
    that highlights overall program health, critical items, and key changes.

    Args:
        context: Report context with status_groups, deliverables, etc.

    Returns:
        Formatted prompt string ready for LLM

    Example:
        >>> context = {"total_deliverables": 12, "status_groups": [...]}
        >>> prompt = build_prompt(context)
        >>> # Send prompt to LLM provider
    """
    total = context.get("total_deliverables", 0)
    status_groups = context.get("status_groups", [])
    report_date = context.get("report_date", "Unknown")

    # Format status breakdown
    status_breakdown = _format_status_breakdown(status_groups)

    # Extract key details from deliverables
    critical_items = _extract_critical_items(status_groups)
    risks_summary = _extract_risks_summary(status_groups)

    prompt = f"""You are analyzing a weekly program status report for a technical program manager.

## Report Metadata
- Report Date: {report_date}
- Total Deliverables: {total}

## Status Breakdown
{status_breakdown}

## Critical Items (Off Track / At Risk)
{critical_items}

## Reported Risks and Issues
{risks_summary}

## Task
Generate a concise executive summary (2-3 sentences) that:

1. **States overall program health** - Is the program on track, at risk, or facing major issues?
2. **Highlights the most critical item** - What single issue requires immediate attention?
3. **Identifies any emerging patterns** - Are there themes across multiple deliverables (e.g., resource constraints, dependency delays)?

## Guidelines
- Be specific and decision-oriented (not generic)
- Focus on actionable insights, not just facts
- Use concrete examples from the data
- Avoid phrases like "the report shows" or "according to the data"
- Write in present tense, as if briefing an executive right now

## Output Format
Return ONLY the executive summary text (2-3 sentences). No preamble, explanation, or formatting."""

    return prompt


def _format_status_breakdown(status_groups: List[Tuple[str, List[Dict]]]) -> str:
    """
    Format status groups into human-readable breakdown.

    Args:
        status_groups: List of (status_name, items) tuples

    Returns:
        Formatted string with status counts
    """
    if not status_groups:
        return "  (No status information available)"

    lines = []
    for status, items in status_groups:
        count = len(items)
        lines.append(f"  - {status}: {count} deliverable{'s' if count != 1 else ''}")

    return "\n".join(lines) if lines else "  (No deliverables)"


def _extract_critical_items(status_groups: List[Tuple[str, List[Dict]]]) -> str:
    """
    Extract and format critical items (Off Track and At Risk).

    Args:
        status_groups: List of (status_name, items) tuples

    Returns:
        Formatted string with critical deliverable details
    """
    critical_statuses = ["Off Track", "At Risk"]
    critical_items = []

    for status, items in status_groups:
        if status in critical_statuses:
            for item in items:
                deliverable = item.get("deliverable", "Unknown")
                priority = item.get("priority", "")
                risks = item.get("risks_issues", "").strip()

                # Build item description
                desc = f"- [{status}] {deliverable}"
                if priority:
                    desc += f" (Priority: {priority})"
                if risks:
                    # Truncate long risk descriptions
                    risks_short = risks[:150] + "..." if len(risks) > 150 else risks
                    desc += f"\n  Risk: {risks_short}"

                critical_items.append(desc)

    if not critical_items:
        return "  (No critical items - all deliverables on track or complete)"

    return "\n".join(critical_items)


def _extract_risks_summary(status_groups: List[Tuple[str, List[Dict]]]) -> str:
    """
    Extract and summarize all reported risks and issues.

    Args:
        status_groups: List of (status_name, items) tuples

    Returns:
        Formatted string with all risks (for LLM to analyze themes)
    """
    all_risks = []

    for status, items in status_groups:
        for item in items:
            deliverable = item.get("deliverable", "Unknown")
            risks = item.get("risks_issues", "").strip()

            if risks and risks.lower() not in [
                "no risks or issues reported this week",
                "none",
                "n/a",
            ]:
                all_risks.append(f"- {deliverable}: {risks}")

    if not all_risks:
        return "  (No risks or issues reported)"

    return "\n".join(all_risks)


def parse_response(response: str) -> Dict[str, Any]:
    """
    Parse LLM response into structured format.

    For executive summaries, we mostly just clean up the response text,
    but this function provides structure for future enhancements
    (e.g., extracting confidence scores, key phrases, etc.).

    Args:
        response: Raw text from LLM

    Returns:
        Dictionary with parsed summary and metadata

    Example:
        >>> response = "Program is on track with 2 at-risk items..."
        >>> parsed = parse_response(response)
        >>> parsed["summary"]
        'Program is on track with 2 at-risk items...'
    """
    # Clean up response
    summary = response.strip()

    # Remove common LLM preambles if present
    preambles = [
        "Here is the executive summary:",
        "Executive Summary:",
        "Summary:",
    ]
    for preamble in preambles:
        if summary.startswith(preamble):
            summary = summary[len(preamble) :].strip()

    return {
        "summary": summary,
        "length": len(summary),
        "sentence_count": summary.count(".") + summary.count("!") + summary.count("?"),
    }
