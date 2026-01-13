# LLM Reasoning Layer - Implementation Plan

**Version:** 1.0.0
**Date:** January 12, 2026
**Status:** Planning

---

## Overview

This document outlines the plan for integrating an LLM-backed reasoning layer into the Chief of Staff Agent, transforming it from a template-based report generator into an intelligent synthesis system.

---

## Current State: Template-Based Architecture

### Current Pipeline
```
CSV → Load → Validate → Transform → Build Context → Render Template → HTML
```

### Current Components
- **Data Layer**: Load, validate, transform structured data
- **Builder Layer**: Group and organize data for templates
- **Template Layer**: Jinja2 templates render HTML from context
- **Output**: Fixed-format HTML reports

### What Works Well
- ✅ Clean separation of concerns
- ✅ Testable, deterministic transformations
- ✅ Configuration-driven behavior
- ✅ Strong validation and error handling

### Limitations
- ❌ No synthesis or insight generation
- ❌ No risk identification or theme extraction
- ❌ Single output format per report type
- ❌ No audience-specific tailoring
- ❌ No action item generation

---

## Target State: Reasoning-Enhanced Architecture

### Enhanced Pipeline
```
CSV → Load → Validate → Transform → Build Context →
  ↓
[NEW] Reasoning Layer → Synthesis → Insights → Risks → Themes →
  ↓
Audience-Specific Rendering → Multiple Outputs (Executive/Technical/Partner)
```

---

## LLM Reasoning Layer Design

### Core Principle
**The reasoning layer enhances but does not replace deterministic data processing.**

### Integration Point
The reasoning layer sits **between** the builder and the renderer:
- Input: Clean, validated, structured data context
- Output: Enriched context with synthesis, insights, and recommendations
- Original data remains unmodified for transparency

### Reasoning Layer Responsibilities

#### 1. Executive Summary Generation
- Synthesize overall program health (2-3 sentences)
- Highlight most critical items requiring attention
- Identify week-over-week changes (if historical data provided)

#### 2. Risk & Theme Extraction
- Analyze "Risks & Issues" fields across all deliverables
- Identify cross-cutting themes (e.g., "resource constraints," "dependency delays")
- Flag anomalies: status mismatches, missing owners, overdue items

#### 3. Insight Generation
- Surface patterns not obvious in tabular view
- Identify deliverables with inconsistent reporting
- Note progress trends (if historical data available)

#### 4. Action Item Recommendations
- Suggest follow-ups based on risks and blockers
- Propose ownership assignments for gaps
- Draft recommended next steps for human review

#### 5. Audience-Specific Synthesis
- **Executive View**: High-level summary, key risks, decisions needed
- **Engineering View**: Technical blockers, dependency chains, resource needs
- **Partner View**: External-facing status, omit internal details

---

## Proposed Module Structure

### New Modules to Add

```
src/report_generator/
├── reasoning/                       # NEW: LLM reasoning layer
│   ├── __init__.py
│   ├── provider.py                  # LLM client abstraction (Anthropic API)
│   ├── synthesizer.py               # Core reasoning orchestration
│   ├── prompts/                     # Prompt templates
│   │   ├── __init__.py
│   │   ├── executive_summary.py    # Executive summary prompt
│   │   ├── risk_analysis.py        # Risk extraction prompt
│   │   ├── theme_extraction.py     # Theme identification prompt
│   │   └── action_items.py         # Action item generation prompt
│   └── config.py                    # Reasoning configuration
│
├── output/
│   ├── renderers/                   # NEW: Multiple output renderers
│   │   ├── __init__.py
│   │   ├── executive_renderer.py   # Executive summary renderer
│   │   ├── technical_renderer.py   # Technical detail renderer
│   │   └── partner_renderer.py     # Partner-safe renderer
│
└── reports/example_report/
    ├── generator.py                 # MODIFIED: Add reasoning step
    └── reasoning_config.py          # NEW: Report-specific reasoning rules
```

---

## Implementation Phases

### Phase 1: Foundation (Week 1)
**Goal:** Basic LLM integration without breaking existing functionality

#### Tasks
1. Create `reasoning/` module structure
2. Implement `provider.py` with Anthropic API client
   - API key management (env vars)
   - Error handling and retries
   - Token usage tracking
3. Create basic `synthesizer.py` with single method: `generate_summary()`
4. Write unit tests with mocked LLM responses
5. Add feature flag to enable/disable reasoning layer

**Deliverable:** Basic LLM call working, no UI changes yet

---

### Phase 2: Executive Summary (Week 2)
**Goal:** Generate executive summary from structured data

#### Tasks
1. Design executive summary prompt template
2. Implement context preparation for LLM
   - Convert structured data to LLM-friendly format
   - Include relevant metadata (dates, counts, status breakdown)
3. Parse LLM response into structured format
4. Add summary to report context
5. Update HTML template to display summary at top
6. Write integration tests

**Deliverable:** Reports now include AI-generated executive summary

---

### Phase 3: Risk & Theme Analysis (Week 3)
**Goal:** Extract risks and themes from "Risks & Issues" fields

#### Tasks
1. Implement risk analysis prompt
2. Extract and aggregate all "Risks & Issues" text
3. Generate structured risk output:
   - Individual risk items
   - Cross-cutting themes
   - Severity assessment
4. Add risks section to report
5. Write tests for risk extraction logic

**Deliverable:** Reports highlight aggregated risks and themes

---

### Phase 4: Multiple Output Formats (Week 4)
**Goal:** Generate audience-specific views from same data

#### Tasks
1. Implement renderer abstraction
2. Create executive renderer (high-level, decision-focused)
3. Create technical renderer (detailed status, blockers)
4. Create partner renderer (external-safe, no internal details)
5. Update CLI to support `--audience` flag
6. Write tests for each renderer

**Deliverable:** One CSV → three different report formats

---

### Phase 5: Action Items (Week 5)
**Goal:** Generate recommended next steps

#### Tasks
1. Implement action item generation prompt
2. Parse suggested actions into structured format
3. Add action items section to reports
4. Include "confidence" indicator for each suggestion
5. Write tests for action generation

**Deliverable:** Reports include AI-suggested action items

---

### Phase 6: Polish & Optimization (Week 6)
**Goal:** Improve performance, cost, and UX

#### Tasks
1. Implement caching for repeated queries
2. Add token usage reporting
3. Optimize prompts for efficiency
4. Add progress indicators for long-running operations
5. Write comprehensive integration tests
6. Update documentation

**Deliverable:** Production-ready reasoning layer

---

## Technical Design Details

### LLM Provider Interface

```python
# reasoning/provider.py

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class LLMProvider(ABC):
    """Abstract interface for LLM providers."""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.0,
    ) -> str:
        """Generate text from prompt."""
        pass

class AnthropicProvider(LLMProvider):
    """Anthropic Claude API provider."""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-5-20250929"):
        self.api_key = api_key
        self.model = model
        self.client = anthropic.Anthropic(api_key=api_key)

    def generate(self, prompt: str, system_prompt: Optional[str] = None,
                 max_tokens: int = 1024, temperature: float = 0.0) -> str:
        """Call Anthropic API."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt or "",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
```

### Synthesizer Interface

```python
# reasoning/synthesizer.py

from typing import Dict, Any, List
from reasoning.provider import LLMProvider
from reasoning.prompts import executive_summary, risk_analysis

class ReportSynthesizer:
    """Orchestrates LLM reasoning over structured report data."""

    def __init__(self, provider: LLMProvider):
        self.provider = provider

    def synthesize(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate insights from report context.

        Args:
            context: Structured data from builder (status_groups, deliverables, etc.)

        Returns:
            Enhanced context with synthesis results
        """
        # Extract executive summary
        summary = self._generate_executive_summary(context)

        # Analyze risks
        risks = self._analyze_risks(context)

        # Return enriched context
        return {
            **context,  # Original data preserved
            "synthesis": {
                "executive_summary": summary,
                "risk_analysis": risks,
                "generated_at": datetime.now().isoformat(),
            }
        }

    def _generate_executive_summary(self, context: Dict[str, Any]) -> str:
        """Generate 2-3 sentence executive summary."""
        prompt = executive_summary.build_prompt(context)
        return self.provider.generate(prompt, temperature=0.0)

    def _analyze_risks(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and categorize risks."""
        prompt = risk_analysis.build_prompt(context)
        response = self.provider.generate(prompt, temperature=0.0)
        return risk_analysis.parse_response(response)
```

### Prompt Template Example

```python
# reasoning/prompts/executive_summary.py

def build_prompt(context: Dict[str, Any]) -> str:
    """Build executive summary prompt from context."""

    total = context["total_deliverables"]
    status_breakdown = _format_status_breakdown(context["status_groups"])

    prompt = f"""You are analyzing a weekly program status report.

## Data Summary
- Total deliverables: {total}
- Status breakdown:
{status_breakdown}

## Task
Generate a 2-3 sentence executive summary that:
1. States overall program health
2. Highlights the most critical item requiring attention
3. Notes any significant week-over-week changes (if data provided)

Be specific and decision-oriented. Focus on what matters most.

## Output Format
Return ONLY the summary text, no preamble or explanation."""

    return prompt

def _format_status_breakdown(status_groups: List) -> str:
    """Format status groups for prompt."""
    lines = []
    for status, items in status_groups:
        lines.append(f"  - {status}: {len(items)} items")
    return "\n".join(lines)
```

---

## Testing Strategy

### Unit Tests (No LLM Calls)
- Mock LLM provider responses
- Test prompt construction logic
- Test response parsing
- Test error handling

```python
# tests/unit/test_synthesizer.py

def test_generate_executive_summary_with_mock():
    """Test summary generation with mocked LLM."""
    mock_provider = MockLLMProvider(
        response="Program is on track with 2 at-risk items requiring attention."
    )
    synthesizer = ReportSynthesizer(mock_provider)

    context = {...}  # Test data
    result = synthesizer.synthesize(context)

    assert "synthesis" in result
    assert "executive_summary" in result["synthesis"]
    assert len(result["synthesis"]["executive_summary"]) > 0
```

### Integration Tests (Real LLM Calls)
- Test with actual API (gated behind env var)
- Validate output quality
- Check token usage

```python
# tests/integration/test_reasoning_pipeline.py

@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("ANTHROPIC_API_KEY"), reason="No API key")
def test_end_to_end_reasoning():
    """Test full reasoning pipeline with real LLM."""
    provider = AnthropicProvider(api_key=os.getenv("ANTHROPIC_API_KEY"))
    synthesizer = ReportSynthesizer(provider)

    # Load fixture data
    context = load_test_context()

    # Run synthesis
    result = synthesizer.synthesize(context)

    # Validate structure
    assert "synthesis" in result
    assert "executive_summary" in result["synthesis"]

    # Validate content quality (basic checks)
    summary = result["synthesis"]["executive_summary"]
    assert len(summary) > 50  # Not empty
    assert len(summary) < 500  # Not too verbose
```

---

## Configuration & Feature Flags

### Environment Variables
```bash
# .env
ANTHROPIC_API_KEY=sk-ant-...
ENABLE_REASONING=true           # Feature flag
REASONING_MODEL=claude-sonnet-4-5-20250929
REASONING_MAX_TOKENS=2048
REASONING_TEMPERATURE=0.0
```

### Report-Specific Configuration
```python
# reports/example_report/reasoning_config.py

REASONING_CONFIG = {
    "enabled": True,  # Enable reasoning for this report
    "features": {
        "executive_summary": True,
        "risk_analysis": True,
        "theme_extraction": True,
        "action_items": False,  # Not yet implemented
    },
    "audience_variants": ["executive", "technical", "partner"],
    "max_tokens": 2048,
    "temperature": 0.0,
}
```

---

## Migration Path

### Backward Compatibility
- Reasoning layer is **opt-in** via feature flag
- Existing reports continue to work unchanged
- `generate()` method gains optional `enable_reasoning=False` parameter

### Example Usage
```python
# Without reasoning (existing behavior)
generator = KPRReportGenerator()
html = generator.generate("data.csv")

# With reasoning (new behavior)
html = generator.generate("data.csv", enable_reasoning=True)

# With audience-specific output
html = generator.generate("data.csv", enable_reasoning=True, audience="executive")
```

---

## Cost & Performance Considerations

### Token Usage Estimation
- **Executive summary**: ~1,500 input tokens + 200 output = ~$0.01 per report
- **Risk analysis**: ~2,000 input + 500 output = ~$0.015 per report
- **Full synthesis**: ~$0.03-0.05 per report

### Optimization Strategies
1. **Prompt engineering**: Minimize input tokens, be specific
2. **Caching**: Cache repeated analyses within same session
3. **Batching**: Analyze multiple items in single call when possible
4. **Model selection**: Use smaller models for simple tasks

---

## Success Criteria

### Phase 1 Success
- [ ] LLM provider interface implemented
- [ ] Basic API integration working
- [ ] Unit tests passing with mocks
- [ ] No breaking changes to existing code

### Phase 2 Success
- [ ] Executive summaries generated for reports
- [ ] Summaries are coherent and relevant
- [ ] Integration tests passing
- [ ] Documentation updated

### Future Success (Phases 3-6)
- [ ] Multi-audience support working
- [ ] Risk analysis identifying real issues
- [ ] Action items are actionable
- [ ] Cost per report < $0.10
- [ ] Response time < 30 seconds

---

## Open Questions

1. **Historical Data**: How do we track week-over-week changes?
   - Store previous report contexts?
   - Separate database for historical trends?

2. **Human Review Workflow**: How do users review and edit AI-generated content?
   - Separate approval step?
   - Direct editing in UI?

3. **Confidence Indicators**: How do we communicate LLM uncertainty?
   - "High confidence" vs "Low confidence" tags?
   - Show source data that informed each insight?

4. **Error Handling**: What happens when LLM fails or returns nonsense?
   - Graceful degradation to template-only mode?
   - Retry logic?

---

## Next Steps

1. Review this plan with stakeholders
2. Set up development environment with Anthropic API key
3. Begin Phase 1: Foundation implementation
4. Create initial test fixtures for LLM testing

---

**Document Owner:** Development Team
**Last Updated:** January 12, 2026
