# Contributing to Report Generator

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please be respectful and constructive in all interactions. We welcome contributors of all experience levels.

## How to Contribute

### Reporting Bugs

1. Check existing [issues](https://github.com/umckinney/report-generator/issues) to avoid duplicates
2. Use the bug report template when creating a new issue
3. Include:
   - Python version and OS
   - Steps to reproduce
   - Expected vs actual behavior
   - Relevant error messages or logs

### Suggesting Features

1. Check existing issues for similar suggestions
2. Use the feature request template
3. Describe the use case and expected behavior
4. Explain why this would benefit other users

### Submitting Changes

1. Fork the repository
2. Create a feature branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make your changes
4. Ensure all tests pass and code quality checks succeed
5. Commit with clear, descriptive messages
6. Push to your fork and open a Pull Request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/report-generator.git
cd report-generator

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install development dependencies
pip install -r requirements-dev.txt
pip install -e .
```

## Development Workflow

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/report_generator --cov-report=html

# Run specific test file
pytest tests/unit/test_loader.py

# Run tests matching a pattern
pytest -k "test_validate"
```

### Code Quality

All code must pass these checks before merging:

```bash
# Format code
black src/ tests/
isort src/ tests/

# Check formatting (as CI does)
black --check src/ tests/
isort --check-only src/ tests/

# Run linter
pylint src/report_generator
```

### Commit Messages

Write clear, concise commit messages:

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Fix bug" not "Fixes bug")
- Reference issues when applicable ("Fix #123: Handle empty CSV")

Examples:
- `Add support for TSV file format`
- `Fix validation error for empty columns`
- `Update documentation for new report types`

## Pull Request Process

1. **Update documentation** if you're changing functionality
2. **Add tests** for new features or bug fixes
3. **Ensure CI passes** - all tests and linting must succeed
4. **Request review** from maintainers
5. **Address feedback** promptly and constructively

### PR Title Format

Use a clear, descriptive title:
- `feat: Add Excel export support`
- `fix: Handle Unicode characters in CSV`
- `docs: Update installation instructions`
- `refactor: Simplify data transformer logic`

## Project Structure

```
src/report_generator/
├── cli.py              # Command-line interface
├── data/               # Data loading and transformation
│   ├── loader.py       # CSV/TSV file loading
│   ├── transformers.py # Data transformation utilities
│   └── validator.py    # Data validation
├── output/             # Output handling
│   └── email_draft.py  # Email draft generation
└── reports/            # Report implementations
    └── example_report/ # Example report type
```

## Adding a New Report Type

1. Create a new directory under `src/report_generator/reports/`:
   ```
   src/report_generator/reports/your_report/
   ├── __init__.py
   ├── config.py      # Field mappings, email config
   ├── builder.py     # Report structure builder
   ├── generator.py   # Main generator class
   ├── template.html  # Jinja2 HTML template
   └── assets/        # Logo, images (optional)
   ```

2. Register in `cli.py`:
   ```python
   REPORT_REGISTRY = {
       "kpr": {...},
       "your-report": {
           "name": "Your Report Name",
           "generator_class": YourReportGenerator,
           "email_config": YOUR_EMAIL_CONFIG,
       },
   }
   ```

3. Add tests in `tests/unit/` and `tests/integration/`

See `docs/ARCHITECTURE.md` for detailed architecture documentation.

## Testing Guidelines

- Write tests for all new functionality
- Maintain or improve code coverage
- Use descriptive test names that explain the scenario
- Include both positive and negative test cases
- Mock external dependencies (file system, email, etc.)

Example test structure:
```python
def test_load_valid_csv_returns_list_of_dicts():
    """Test that loading a valid CSV returns expected data structure."""
    loader = TabularDataLoader()
    data = loader.load("tests/fixtures/mock_data.csv")

    assert isinstance(data, list)
    assert len(data) > 0
    assert isinstance(data[0], dict)
```

## Questions?

Feel free to open an issue for questions or join discussions. We're happy to help!
