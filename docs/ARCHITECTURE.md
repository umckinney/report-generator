# Report Generator - Architecture Documentation

**Version 1.0.0**  
**Last Updated:** 29 December 2025  
**Audience:** Developers and maintainers

---

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Project Structure](#project-structure)
4. [Core Components](#core-components)
5. [Data Flow](#data-flow)
6. [Adding New Reports](#adding-new-reports)
7. [Configuration Management](#configuration-management)
8. [Testing Strategy](#testing-strategy)
9. [Packaging & Distribution](#packaging--distribution)
10. [Maintenance Guide](#maintenance-guide)

---

## Overview

### Design Philosophy

The KPR Report Generator follows these key principles:

1. **Separation of Concerns**: Data processing, business logic, and presentation are cleanly separated
2. **Configuration-Driven**: Report-specific logic lives in configuration files, not hardcoded
3. **Test-Driven**: 59 tests with 93% coverage on core components
4. **Extensible**: New report types can be added without modifying core infrastructure
5. **Maintainable**: Built with handoff to non-engineer (TPM) in mind

### Technology Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Language | Python | 3.12+ | Core application |
| Data Processing | pandas | 2.x | CSV loading & manipulation |
| Templating | Jinja2 | 3.x | HTML report generation |
| Packaging | PyInstaller | 6.x | Standalone executable |
| Testing | pytest | 8.x | Unit & integration tests |
| Code Quality | black, isort | Latest | Code formatting |

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

See full documentation for detailed component descriptions.

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
