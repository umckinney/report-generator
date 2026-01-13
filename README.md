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

**Current State**: Phase 3 Complete - Risk & Theme Analysis now available! ✨

**Latest Features:**
- ✅ AI-powered executive summary generation
- ✅ AI-powered risk & theme analysis with cross-cutting pattern detection
- ✅ Multi-provider support (Anthropic Claude, ready for OpenAI)
- ✅ Beautiful visual integration with AI badges and severity indicators
- ✅ Feature flag system for opt-in AI features
- ✅ Graceful degradation and error handling
- ✅ Comprehensive testing (188 tests, 97% coverage)

The system includes both deterministic report generation and optional AI-powered synthesis for intelligent insights.

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

**Without AI (traditional report generation):**
```bash
# Generate a report from CSV
report-generator generate --report kpr --csv data.csv

# Generate and open as email draft (macOS)
report-generator generate --report kpr --csv data.csv --email
```

**With AI-Powered Executive Summaries:**
```bash
# Set your Anthropic API key
export ANTHROPIC_API_KEY="your-key-here"

# Enable AI reasoning
export ENABLE_REASONING=true

# Generate report with AI insights
report-generator generate --report kpr --csv data.csv

# Or run the demo
python demo_executive_summary.py
```

**Other commands:**
```bash
# List available report types
report-generator list-reports

# Run as a module
python -m report_generator generate --report kpr --csv data.csv
```

## AI Features 🤖

### Executive Summary Generation

The Chief of Staff Agent can automatically generate intelligent executive summaries of your reports using LLM reasoning.

**What it does:**
- Analyzes status breakdown across all deliverables
- Identifies critical items requiring attention (Off Track, At Risk)
- Extracts themes from risks and issues
- Generates a 2-3 sentence executive summary
- Displays prominently at the top of reports with "AI-Generated" badge

**Example output:**
> "Program shows mixed health with 1 off-track and 1 at-risk deliverable requiring immediate attention. The API Gateway Upgrade is off track but progressing on alignment, while the Data Retention Process is at risk due to current processing hold. The Real-time Fraud Detection system successfully launched, providing a positive completion milestone."

**Configuration:**
```bash
# Required: Set API key
export ANTHROPIC_API_KEY="your-key-here"

# Enable reasoning (default: false)
export ENABLE_REASONING=true

# Optional: Configure model and parameters
export REASONING_PROVIDER=anthropic  # default
export REASONING_MAX_TOKENS=2048     # default
export REASONING_TEMPERATURE=0.0     # default (deterministic)
```

**Cost:** ~$0.01-0.03 per report (very affordable with Claude Sonnet 4.5)

**Privacy:** Your data is sent to Anthropic's API for processing. See [Anthropic's privacy policy](https://www.anthropic.com/privacy) for details.

### Risk & Theme Analysis

The Chief of Staff Agent can analyze all risks and issues across deliverables to identify patterns, critical items, and anomalies.

**What it does:**
- Identifies cross-cutting themes affecting multiple deliverables (e.g., "resource constraints", "dependency delays")
- Flags critical risks requiring immediate attention
- Detects anomalies (vague descriptions, status mismatches, missing information)
- Provides severity assessment (high/medium/low) for each theme
- Displays in a dedicated "Risk & Theme Analysis" section with color-coded severity badges

**Example output:**

*Cross-Cutting Themes:*
- **Resource Constraints (HIGH)** - Multiple teams facing staffing issues
  - Affects: API Gateway Upgrade, Data Pipeline Modernization

*Critical Risks:*
- **API Gateway Upgrade** - Team understaffed by 2 engineers
  - Why Critical: Impacts Q1 launch timeline

*Anomalies:*
- **User Auth System** - Marked "On Track" but reports major security concerns

**Configuration:**
Same as Executive Summary - just ensure `ENABLE_REASONING=true`. Risk analysis is enabled by default when reasoning is active.

### Coming Soon

- **Multi-Audience Support**: Generate executive, technical, and partner views
- **Action Item Recommendations**: AI-suggested next steps
- **Historical Trend Analysis**: Week-over-week change detection

## Development

### Prerequisites
- Python 3.10+
- macOS (for email integration) or Linux
- Anthropic API key (optional, for AI features)

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
chief-of-staff-agent/
├── src/report_generator/
│   ├── cli.py                    # Command-line interface
│   ├── data/                     # Data loading & transformation
│   │   ├── loader.py             # CSV/TSV file loading
│   │   ├── transformers.py       # Data transformation utilities
│   │   └── validator.py          # Data validation
│   ├── reasoning/                # 🆕 AI reasoning layer
│   │   ├── provider.py           # LLM provider interface & implementations
│   │   ├── config.py             # Feature flags and configuration
│   │   ├── synthesizer.py        # Report synthesis orchestration
│   │   └── prompts/              # Prompt engineering templates
│   │       └── executive_summary.py
│   ├── output/                   # Output handling
│   │   └── email_draft.py        # Email draft generation
│   └── reports/
│       └── example_report/       # Example report implementation
│           ├── builder.py        # Report structure builder
│           ├── config.py         # Configuration & mappings
│           ├── generator.py      # Main generator orchestration
│           ├── template.html     # HTML email template (AI-enhanced)
│           └── assets/           # Logo and images
├── tests/
│   ├── unit/                     # Unit tests (162 tests)
│   ├── integration/              # Integration tests
│   └── fixtures/                 # Test data
├── docs/                         # Documentation
│   ├── LLM_REASONING_PLAN.md     # 🆕 AI implementation plan
│   └── CHIEF_OF_STAFF_OVERVIEW.md # 🆕 Project vision
├── demo_executive_summary.py     # 🆕 Live demo script
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

### AI Features

**Executive summary not appearing:**
- Ensure `ENABLE_REASONING=true` is set
- Verify `ANTHROPIC_API_KEY` is set correctly
- Check console output for reasoning layer status
- Summary only appears if reasoning succeeds (graceful degradation)

**API errors:**
- Verify API key is valid: `echo $ANTHROPIC_API_KEY`
- Check account has credits remaining
- Review rate limits (shouldn't be an issue for typical use)
- Check firewall/proxy settings

**Cost concerns:**
- Each report costs ~$0.01-0.03 with Claude Sonnet 4.5
- Token usage is logged in console output
- Disable with `unset ENABLE_REASONING` anytime

### General Issues

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

### Core
- **Python 3.10+**: Core language
- **pandas**: CSV processing & data manipulation
- **Jinja2**: HTML templating engine
- **pytest**: Testing framework (162 tests, 95% coverage)

### AI Features (Optional)
- **Anthropic Claude API**: LLM reasoning (Sonnet 4.5)
- **Multi-provider architecture**: Ready for OpenAI, local models, etc.
- **Prompt engineering**: Structured templates for consistent outputs
- **Token tracking**: Built-in usage monitoring
