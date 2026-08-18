# Contributing to READI

Thank you for your interest in contributing! This guide covers everything you need to get started.

---

## Development Setup

**Prerequisites:** Python 3.11+, [uv](https://docs.astral.sh/uv/), Git with [git-lfs](https://git-lfs.com/).

```bash
git clone https://github.com/IBM/READI.git
cd READI

# Create virtual environment and install all dependencies (including dev extras)
uv venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"

# Install pre-commit hooks
prek install
```

---

## Running Tests

```bash
# Run the full test suite
pytest

# Run a specific test file
pytest tests/readi/test_analyzer.py -v

# Run with coverage report
pytest --cov=risk_assessment --cov-report=html
```

---

## Linting and Formatting

The project uses [Ruff](https://docs.astral.sh/ruff/) for linting and formatting.

```bash
# Check for lint errors
ruff check src/ tests/

# Auto-fix lint errors
ruff check --fix src/ tests/

# Format code
ruff format src/ tests/
```

Pre-commit hooks run these checks automatically on every commit. To run them manually:

```bash
pre-commit run --all-files
```

---

## Code Style

- Follow existing patterns in the surrounding code.
- All public classes, methods, and module-level functions must have docstrings.
- Use Google-style docstrings with `Args:`, `Returns:`, and `Raises:` sections where applicable.
- Type hints are required on all function signatures.
- Line length limit is 120 characters (enforced by Ruff).

---

## Pull Request Process

1. **Branch** off `main` using a descriptive name, e.g. `feat/italian-fiscal-code` or `fix/email-regex`.
2. **Write tests** for any new functionality. PRs without tests for new features will not be merged.
3. **Ensure all checks pass** locally before opening a PR:
   ```bash
   prek run --all-files
   pytest
   ```
4. **Open a Pull Request** against `main`. Fill in the PR template, linking any related issues.
5. At least one maintainer review is required before merging.

---

## Reporting Issues

Use [GitHub Issues](https://github.com/IBM/READI/issues) to report bugs or request features. Please include:
- A minimal reproducible example for bugs.
- The Python version and OS you are using.
- The full error traceback if applicable.

---

## License

By contributing, you agree that your contributions will be licensed under the [Apache License 2.0](LICENSE).
