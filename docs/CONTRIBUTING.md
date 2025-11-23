# Contributing to Google Maps MCP Server

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Release Process](#release-process)

## Code of Conduct

### Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards

**Positive behaviors include:**

- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Unacceptable behaviors include:**

- Trolling, insulting/derogatory comments, and personal or political attacks
- Public or private harassment
- Publishing others' private information without permission
- Other conduct which could reasonably be considered inappropriate

## Getting Started

### Prerequisites

- Python 3.10 or higher
- uv package manager
- Git
- Google Maps API key (for testing)

### Setup

1. **Fork the repository** on GitHub

2. **Clone your fork:**

   ```bash
   git clone https://github.com/YOUR_USERNAME/google-maps-mcp-server.git
   cd google-maps-mcp-server
   ```

3. **Add upstream remote:**

   ```bash
   git remote add upstream https://github.com/ettysekhon/google-maps-mcp-server.git
   ```

4. **Install dependencies:**

   ```bash
   uv sync --extra dev --extra docs
   ```

5. **Install pre-commit hooks:**

   ```bash
   uv run pre-commit install
   ```

6. **Create a `.env` file:**

   ```bash
   cp .env.example .env
   # Edit .env and add your Google Maps API key
   ```

## Development Workflow

### Creating a Branch

```bash
# Update your main branch
git checkout main
git pull upstream main

# Create a feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/issue-description
```

### Branch Naming Conventions

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Test additions or modifications
- `chore/` - Maintenance tasks

### Making Changes

1. Make your changes in your feature branch
2. Add tests for any new functionality
3. Ensure all tests pass
4. Update documentation as needed
5. Commit your changes with clear messages

### Commit Message Format

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```text
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Maintenance tasks

**Examples:**

```text
feat(places): add support for place photos

Add new tool to retrieve place photos from Places API.
Includes tests and documentation.

Closes #123

fix(geocoding): handle empty address components

Previously crashed when address components were missing.
Now returns graceful error message.

Fixes #456
```

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://peps.python.org/pep-0008/) with some modifications:

- Line length: 100 characters (enforced by Black)
- Use double quotes for strings
- Use trailing commas in multi-line structures

### Code Formatting

We use **Black** for code formatting:

```bash
# Format all code
uv run black src tests

# Check formatting without changes
uv run black --check src tests
```

### Linting

We use **Ruff** for linting:

```bash
# Lint code
uv run ruff check src tests

# Auto-fix issues
uv run ruff check src tests --fix
```

### Type Checking

We use **mypy** for static type checking:

```bash
# Type check
uv run mypy src
```

### Code Quality Checklist

Before committing, ensure:

- [ ] Code is formatted with Black
- [ ] No linting errors from Ruff
- [ ] Type checking passes with mypy
- [ ] All tests pass
- [ ] Test coverage is maintained or improved
- [ ] Documentation is updated

### Quick Quality Check

```bash
# Run all checks at once
uv run black src tests && \
uv run ruff check src tests && \
uv run mypy src && \
uv run pytest
```

## Testing

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html --cov-report=term

# Run specific test file
uv run pytest tests/unit/test_places.py

# Run tests matching pattern
uv run pytest -k "test_geocoding"

# Run only unit tests (skip integration)
uv run pytest -m "not integration"

# Run with verbose output
uv run pytest -v
```

### Writing Tests

#### Test Structure

```python
# tests/unit/test_your_feature.py
"""Unit tests for your feature."""
import pytest
from google_maps_mcp_server.your_module import YourClass


class TestYourClass:
    """Test suite for YourClass."""

    def test_basic_functionality(self):
        """Test basic functionality."""
        # Arrange
        obj = YourClass()

        # Act
        result = obj.some_method()

        # Assert
        assert result == expected_value

    @pytest.mark.asyncio
    async def test_async_functionality(self):
        """Test async functionality."""
        obj = YourClass()
        result = await obj.async_method()
        assert result is not None
```

#### Test Coverage Requirements

- Minimum coverage: 80% overall
- New code should have >90% coverage
- Critical paths must have 100% coverage

### Integration Tests

Integration tests require a real Google Maps API key:

```bash
# Run integration tests
GOOGLE_MAPS_API_KEY=your_key uv run pytest -m integration
```

**Note:** Integration tests are not run in CI by default to avoid API charges.

## Pull Request Process

### Before Submitting

1. **Update from upstream:**

   ```bash
   git checkout main
   git pull upstream main
   git checkout your-feature-branch
   git rebase main
   ```

2. **Run full test suite:**

   ```bash
   uv run pytest
   ```

3. **Check code quality:**

   ```bash
   uv run black src tests
   uv run ruff check src tests
   uv run mypy src
   ```

4. **Update documentation** if needed

5. **Update CHANGELOG.md** with your changes

### Submitting a Pull Request

1. Push your branch to your fork:

   ```bash
   git push origin your-feature-branch
   ```

2. Go to the [repository on GitHub](https://github.com/ettysekhon/google-maps-mcp-server)

3. Click "New Pull Request"

4. Select your fork and branch

5. Fill out the PR template:
   - **Title**: Clear, concise description
   - **Description**:
     - What changes were made
     - Why the changes were needed
     - Any breaking changes
     - Related issues
   - **Checklist**: Complete all items

### PR Template

```markdown
## Description
Brief description of changes

## Motivation and Context
Why is this change required? What problem does it solve?

## Type of Change
- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to change)
- [ ] Documentation update

## How Has This Been Tested?
Describe the tests you ran and test configurations.

## Checklist
- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] Any dependent changes have been merged and published

## Screenshots (if applicable)
```

### Review Process

1. **Automated Checks**: CI must pass
   - All tests pass
   - Code quality checks pass
   - Coverage requirements met

2. **Code Review**: At least one maintainer approval required
   - Code quality
   - Test coverage
   - Documentation
   - Design decisions

3. **Changes Requested**: Address feedback and push updates

4. **Approval**: Once approved, a maintainer will merge

### After Your PR is Merged

1. **Delete your branch:**

   ```bash
   git branch -d your-feature-branch
   git push origin --delete your-feature-branch
   ```

2. **Update your main branch:**

   ```bash
   git checkout main
   git pull upstream main
   ```

## Release Process

Releases are managed by maintainers following semantic versioning:

- **MAJOR**: Breaking changes
- **MINOR**: New features (backwards compatible)
- **PATCH**: Bug fixes (backwards compatible)

### Version Bumping

```bash
# Update version in pyproject.toml
# Update CHANGELOG.md
# Commit and tag
git commit -am "chore: bump version to X.Y.Z"
git tag vX.Y.Z
git push upstream main --tags
```

## Documentation

### Updating Documentation

- **Code documentation**: Use docstrings (Google style)
- **README.md**: Update for new features or changes
- **API.md**: Update tool documentation
- **Examples**: Add examples for new features

### Docstring Format

```python
def example_function(param1: str, param2: int) -> bool:
    """
    Brief description of function.

    Longer description if needed, explaining the function's
    purpose, behavior, and any important notes.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When param1 is empty
        TypeError: When param2 is negative

    Example:
        >>> example_function("test", 42)
        True
    """
    pass
```

## Questions?

- 💬 [GitHub Discussions](https://github.com/ettysekhon/google-maps-mcp-server/discussions)
- 📧 Email: <etty.sekhon@gmail.com>

## Recognition

Contributors will be recognized in:

- README.md contributors section
- Release notes
- Project acknowledgments

Thank you for contributing! 🎉
