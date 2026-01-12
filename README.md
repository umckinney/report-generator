# Chief of Staff Agent

[![CI](https://github.com/umckinney/report-generator/actions/workflows/ci.yml/badge.svg)](https://github.com/umckinney/report-generator/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

An intelligent coordination and synthesis system that transforms structured program data into coherent narratives, decision-ready summaries, and actionable insights for leaders and program owners.

## Overview

The **Chief of Staff (CoS) Agent** augments human judgment by consolidating fragmented inputs from CSV/TSV exports into unified, intelligent reports tailored for different audiences. It reduces coordination overhead, surfaces meaningful signals, and proposes concrete next steps—all while remaining transparent, auditable, and human-reviewed.

**Core Capabilities:**
- **Intelligent Synthesis**: LLM-powered reasoning extracts themes, risks, and insights from structured data
- **Multi-Audience Support**: Generate executive summaries, technical deep-dives, and partner-safe updates from the same source
- **Action-Oriented**: Proposes follow-up actions, ownership gaps, and draft artifacts for review
- **Trustworthy & Testable**: Built with TDD, explicit inputs, deterministic transformations, and transparent uncertainty handling
- **Extensible Architecture**: Support technical programs, operational reviews, or any cross-functional initiative by swapping report definitions

## Project Status

**Current State**: Foundation layer complete (data ingestion, validation, transformation, templating)

**In Progress**: LLM reasoning layer integration (see [LLM_REASONING_PLAN.md](docs/LLM_REASONING_PLAN.md))

The system currently operates as a deterministic report generator. The reasoning layer is being added incrementally to enable intelligent synthesis while preserving the reliable data pipeline.

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/umckinney/report-generator.git
cd report-generator

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install the package
pip install -e .
```

### Basic Usage

```bash
# Generate a report from CSV
report-generator generate --report kpr --csv data.csv

# Generate and open as email draft (macOS)
report-generator generate --report kpr --csv data.csv --email

# List available report types
report-generator list-reports
```

Or run as a module:
```bash
python -m report_generator generate --report kpr --csv data.csv --email
```

## Development

### Prerequisites
- Python 3.10+
- macOS (for email integration) or Linux

### Setup

```bash
# Clone and enter directory
git clone https://github.com/umckinney/report-generator.git
cd report-generator

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install with development dependencies
pip install -r requirements-dev.txt
pip install -e .
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/report_generator --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Code Quality

```bash
# Format code
black src/ tests/
isort src/ tests/

# Run linter
pylint src/report_generator

# Run all checks (as CI does)
black --check src/ tests/
isort --check-only src/ tests/
pylint src/report_generator --fail-under=9.0
```

## Project Structure

```
report-generator/
├── src/report_generator/
│   ├── cli.py                    # Command-line interface
│   ├── data/                     # Data loading & transformation
│   │   ├── loader.py             # CSV/TSV file loading
│   │   ├── transformers.py       # Data transformation utilities
│   │   └── validator.py          # Data validation
│   ├── output/                   # Output handling
│   │   └── email_draft.py        # Email draft generation
│   └── reports/
│       └── example_report/       # Example report implementation
│           ├── builder.py        # Report structure builder
│           ├── config.py         # Configuration & mappings
│           ├── generator.py      # Main generator orchestration
│           ├── template.html     # HTML email template
│           └── assets/           # Logo and images
├── tests/
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   └── fixtures/                 # Test data
├── docs/                         # Documentation
└── outputs/                      # Generated reports (gitignored)
```

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed architecture documentation.

**High-level flow:**
```
CSV Export → Load → Validate → Transform → Build Context → Render Template → Email Draft
```

## Configuration

Email recipients and report settings are configured in the report's `config.py`:

```python
# src/report_generator/reports/example_report/config.py
EMAIL_CONFIG = {
    "to": ["your-team@example.com"],
    "cc": [],
    "subject": "Weekly Key Priorities Report - {date}",
}
```

## Adding New Reports

1. Create a new folder: `src/report_generator/reports/your_report/`
2. Add the required files:
   - `config.py` - Configuration and field mappings
   - `builder.py` - Report structure builder
   - `generator.py` - Main generator class
   - `template.html` - Jinja2 HTML template
3. Register in `cli.py` REPORT_REGISTRY

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed instructions.

## Troubleshooting

### Email draft not opening (macOS)
- Ensure Mail.app is configured with an email account
- Grant automation permissions: System Settings → Privacy & Security → Automation

### CSV parsing errors
- Verify the CSV uses comma or tab delimiters
- Check for consistent column counts across rows
- Ensure the file is UTF-8 encoded

### Template rendering issues
- Check Jinja2 syntax in `template.html`
- Verify all referenced variables exist in the context

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Tech Stack

- **Python 3.10+**: Core language
- **pandas**: CSV processing
- **Jinja2**: HTML templating
- **pytest**: Testing framework
