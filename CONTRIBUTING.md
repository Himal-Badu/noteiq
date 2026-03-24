# Contributing to NoteIQ

Thank you for your interest in contributing to NoteIQ! This document provides guidelines for contributing.

## Code of Conduct

We are committed to providing a welcoming and inclusive experience. Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before participating.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported
2. Create a detailed issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details

### Suggesting Features

1. Check existing issues and discussions
2. Open a new issue with:
   - Clear title starting with "Feature:"
   - Detailed description
   - Use cases
   - Potential implementation ideas

### Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run tests: `pytest`
5. Commit with clear messages
6. Push and create a PR

## Development Setup

```bash
# Clone and setup
git clone https://github.com/himalbadu/noteiq.git
cd noteiq

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
pytest

# Format code
black .
isort .
flake8 .
```

## Coding Standards

- **Type hints** - Use type hints for all function signatures
- **Docstrings** - Use Google-style docstrings
- **Tests** - Write tests for new features
- **Commits** - Write clear, descriptive commit messages

## Commit Message Format

```
type(scope): description

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

## Questions?

- Open an issue for bugs/feature requests
- Start a discussion for questions
- Email: himal@noteiq.app