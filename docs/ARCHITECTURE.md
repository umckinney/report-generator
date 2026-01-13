# Chief of Staff Agent - Architecture Documentation

**Version 2.0.0**
**Last Updated:** 12 January 2026
**Audience:** Developers and maintainers

---

## Table of Contents

1. [Overview](#overview)
2. [Evolution to Chief of Staff Agent](#evolution-to-chief-of-staff-agent)
3. [System Architecture](#system-architecture)
4. [Project Structure](#project-structure)
5. [Core Components](#core-components)
6. [Data Flow](#data-flow)
7. [Adding New Reports](#adding-new-reports)
8. [Configuration Management](#configuration-management)
9. [Testing Strategy](#testing-strategy)
10. [Packaging & Distribution](#packaging--distribution)
11. [Maintenance Guide](#maintenance-guide)

---

## Overview

### Design Philosophy

The Chief of Staff Agent follows these key principles:

1. **Human-in-the-Loop**: The agent assists and proposes; humans decide
2. **Separation of Concerns**: Data processing, reasoning, and presentation are cleanly separated
3. **Configuration-Driven**: Report-specific logic lives in configuration files, not hardcoded
4. **Test-Driven Development**: 93% coverage on core components, all new features developed with TDD
5. **Extensible by Design**: New report types, reasoning capabilities, and outputs can be added incrementally
6. **Transparent & Auditable**: Explicit inputs, clear separation between source data and generated insights
7. **Deterministic Where Possible**: LLM reasoning is bounded and validated; core data pipeline remains deterministic

### Technology Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Language | Python | 3.12+ | Core application |
| Data Processing | pandas | 2.x | CSV loading & manipulation |
| LLM Provider | Anthropic Claude | Sonnet 4.5 | Reasoning & synthesis |
| Templating | Jinja2 | 3.x | HTML report generation |
| Packaging | PyInstaller | 6.x | Standalone executable |
| Testing | pytest | 8.x | Unit & integration tests |
| Code Quality | black, isort | Latest | Code formatting |

---

## Evolution to Chief of Staff Agent

### From Report Generator to Intelligent Agent

The system has evolved from a simple template-based report generator into an intelligent coordination agent:

**Phase 1 (Complete)**: Deterministic Report Generator
- CSV ingestion, validation, transformation
- Template-based HTML rendering
- Email integration
- 93% test coverage

**Phase 2 (Complete)**: LLM Reasoning Layer
- ✅ Executive summary generation
- ✅ Risk & theme extraction
- ✅ Insight synthesis
- ✅ Multi-provider architecture

**Phase 3 (Complete)**: Risk & Theme Analysis
- ✅ Cross-cutting theme identification
- ✅ Critical risk detection
- ✅ Anomaly flagging
- ✅ Severity assessment

**Phase 4 (Complete)**: Multi-Audience Support
- ✅ Executive renderer (decision-focused)
- ✅ Technical renderer (complete details)
- ✅ Partner renderer (external-safe)
- ✅ Audience-specific templates
- ✅ Automatic sanitization

**Phase 5 (Complete)**: Action Item Recommendations
- ✅ AI-powered action item generation
- ✅ Confidence-rated recommendations
- ✅ Owner assignment and success criteria
- ✅ Specific, implementable suggestions
- ✅ Visual display with confidence badges

**Phase 6 (Planned)**: Polish & Optimization
- Historical trend analysis
- Caching for repeated queries
- Token usage optimization
- Progress indicators

### What Makes It a "Chief of Staff" Agent?

Traditional report generators transform data into fixed templates. The Chief of Staff Agent goes further by:

1. **Understanding Context**: Analyzes relationships between data points, not just formatting them
2. **Synthesizing Insights**: Extracts themes, patterns, and anomalies across deliverables
3. **Tailoring Communication**: Adapts messaging for executives, engineers, and external partners
4. **Proposing Actions**: Suggests concrete next steps based on status and risks
5. **Maintaining Trust**: Keeps humans in the loop, shows its work, handles uncertainty explicitly

See [LLM_REASONING_PLAN.md](LLM_REASONING_PLAN.md) for detailed implementation plan.

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CLI Interface                            │
│                   (cli.py, __main__.py)                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Report Generator                            │
│              (example_report/)                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Config   │  │ Builder  │  │Generator │  │ Template │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   Data Pipeline                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │  Loader  │─▶│Validator │─▶│Transform │                  │
│  └──────────┘  └──────────┘  └──────────┘                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   Output Handler                             │
│                  (email_draft.py)                            │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Layer | Responsibility | Examples |
|-------|----------------|----------|
| **CLI** | User interface, command parsing, orchestration | `cli.py`, `__main__.py` |
| **Report** | Report-specific logic, configuration | `config.py`, `builder.py`, `generator.py` |
| **Data** | Generic data operations | `loader.py`, `validator.py`, `transformers.py` |
| **Output** | Delivery mechanisms | `email_draft.py` |

---

## Project Structure

```
report_generator_v2/
│
├── src/report_generator/           # Source code
│   ├── __init__.py
│   ├── __main__.py                 # Entry point for python -m
│   ├── cli.py                      # CLI interface & commands
│   │
│   ├── data/                       # Generic data processing
│   │   ├── __init__.py
│   │   ├── loader.py               # CSV/TSV loading with BOM handling
│   │   ├── validator.py            # Structure validation
│   │   └── transformers.py         # Generic transformations
│   │
│   ├── output/                     # Output handlers
│   │   ├── __init__.py
│   │   └── email_draft.py          # Email draft generation (.eml)
│   │
│   ├── reports/                    # Report-specific implementations
│   │   ├── __init__.py
│   │   └── example_report/  # KPR report
│   │       ├── __init__.py
│   │       ├── config.py           # Field mappings, display config
│   │       ├── builder.py          # Report structure builder
│   │       ├── generator.py        # Orchestrates full pipeline
│   │       ├── template.html       # Jinja2 HTML template
│   │       └── assets/
│   │           └── logo.png
│   │
│   └── utils/                      # Shared utilities (empty for now)
│       └── __init__.py
│
├── tests/                          # Test suite
│   ├── fixtures/                   # Test data
│   │   ├── mock_data.csv
│   │   └── KeyPrioritiesReview-10.csv
│   ├── unit/                       # Unit tests
│   │   ├── test_loader.py
│   │   ├── test_validator.py
│   │   ├── test_transformers.py
│   │   ├── test_kpr_builder.py
│   │   ├── test_kpr_template.py
│   │   └── test_email_draft.py
│   └── integration/                # Integration tests
│       └── test_kpr_pipeline.py
│
├── docs/                           # Documentation
│   ├── USER_GUIDE.md
│   └── ARCHITECTURE.md (this file)
│
├── outputs/                        # Generated reports (gitignored)
├── dist/                           # Built executables (gitignored)
├── build/                          # Build artifacts (gitignored)
│
├── README.md                       # Project overview
├── requirements.txt                # Python dependencies
├── pytest.ini                      # Pytest configuration
├── kpr_report_generator.spec      # PyInstaller spec
└── package.sh                      # Distribution packaging script
```

---

## Core Components

### Multi-Audience Rendering System

**Location:** `src/report_generator/output/renderers/`

The multi-audience rendering system allows generation of three different views from the same report data:

#### Renderer Architecture

```python
AudienceRenderer (Abstract Base Class)
├── ExecutiveRenderer
├── TechnicalRenderer
└── PartnerRenderer
```

**Base Renderer Interface:**
- `get_template_name()` - Returns template filename
- `get_audience_name()` - Returns human-readable audience name
- `transform_context(context)` - Transforms data for specific audience
- `render(context, logo_base64)` - Renders final HTML

#### Renderer Types

**1. ExecutiveRenderer** (`renderers/executive.py`)
- **Purpose:** High-level, decision-focused view for executives
- **Template:** `template_executive.html`
- **Transformations:**
  - Filters to show only critical items (Off Track, At Risk)
  - Hides "On Track" items (shows count only)
  - Emphasizes AI synthesis and risk themes
  - Simplifies deliverable details
- **Use Cases:** Board updates, executive reviews, decision meetings

**2. TechnicalRenderer** (`renderers/technical.py`)
- **Purpose:** Complete details for engineering teams
- **Template:** `template_technical.html`
- **Transformations:**
  - Shows ALL deliverables with full details
  - Includes technical updates, blockers, dependencies
  - Expands risk analysis for debugging
  - Preserves all metadata
- **Use Cases:** Sprint planning, technical reviews, engineering updates

**3. PartnerRenderer** (`renderers/partner.py`)
- **Purpose:** External-safe, sanitized information for partners
- **Template:** `template_partner.html`
- **Transformations:**
  - Hides internal lead names (shows "Internal Team")
  - Filters high-severity risks and anomalies
  - Shows aggregate status counts (not individual items)
  - Truncates long internal descriptions
- **Use Cases:** Client updates, partner status, external communications

#### Integration with Generator

The `KPRReportGenerator` integrates renderers via the `audience` parameter:

```python
generator = KPRReportGenerator()

# Executive view
html = generator.generate("data.csv", audience="executive")

# Technical view
html = generator.generate("data.csv", audience="technical")

# Partner view
html = generator.generate("data.csv", audience="partner")

# Default view (backward compatible)
html = generator.generate("data.csv")  # Uses original template
```

**Benefits:**
- **One Source, Multiple Views:** Same CSV generates three different reports
- **Consistent Data:** All audiences see the same underlying data
- **Automatic Sanitization:** Partner view automatically filters sensitive info
- **Type-Safe:** Uses Python Literal types for audience validation
- **Extensible:** Add new audiences by extending `AudienceRenderer`

---

## Data Flow

### Complete Pipeline (KPR Report)

```
Airtable CSV → Load → Validate → Transform → Clean → Build Context → Render → Save → Email
```

---

## Adding New Reports

See full documentation for step-by-step guide.

---

## Configuration Management

### Configuration Philosophy

**Principle:** Configuration should be:
1. **Declarative:** What, not how
2. **Centralized:** One place per report
3. **Type-safe:** Use dictionaries with known structure
4. **Documented:** Comments explain purpose

---

## Testing Strategy

### Test Coverage

**Current Coverage:** 93% on core components

---

## Packaging & Distribution

### PyInstaller Configuration

**Spec file:** `kpr_report_generator.spec`

---

## Maintenance Guide

### Common Maintenance Tasks

See full documentation for maintenance procedures.

---

## Best Practices

### Code Style

- **Black** for formatting
- **isort** for imports
- **Docstrings:** All public functions/classes
- **Type hints:** Use when it improves clarity

---

## Appendix

### Key Design Decisions

See full documentation for design rationale.

---

**Document Version:** 1.0.0
**Last Updated:** 29 December 2025
