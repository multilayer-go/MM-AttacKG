# Contributing to MM-AttacKG

Thank you for your interest in contributing to MM-AttacKG! This document provides guidelines for contributing to the project.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and collaborative environment.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)

### Suggesting Enhancements

Enhancement suggestions are welcome! Please create an issue describing:
- The proposed feature
- Use case and benefits
- Possible implementation approach

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following our coding standards
3. **Add tests** for new functionality
4. **Update documentation** as needed
5. **Ensure tests pass**: `pytest tests/`
6. **Submit a pull request**

## Development Setup

1. Clone your fork:
```bash
git clone https://github.com/your-username/MM-AttacKG.git
cd MM-AttacKG
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
pip install -e .
```

4. Configure API keys:
```bash
cp config/config.example.yaml config/config.yaml
# Edit config/config.yaml with your keys
```

## Coding Standards

### Python Style Guide

- Follow [PEP 8](https://pep8.org/)
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Maximum line length: 100 characters

### Code Formatting

We use `black` for code formatting:
```bash
black src/ tests/
```

### Type Hints

Use type hints where possible:
```python
def process_image(image_path: str, config: dict) -> dict:
    """Process an image and return results."""
    pass
```

### Documentation

- Add docstrings in Google style format
- Update README.md for user-facing changes
- Update API.md for API changes

Example docstring:
```python
def generate_questions(image_path: str, image_type: str) -> List[str]:
    """Generate questions based on image type.
    
    Args:
        image_path: Path to the image file
        image_type: Category of the image (one of 7 types)
        
    Returns:
        List of generated questions
        
    Raises:
        ValueError: If image_type is not recognized
    """
    pass
```

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_question_generation.py
```

### Writing Tests

- Place tests in `tests/` directory
- Name test files: `test_*.py`
- Name test functions: `test_*`
- Use fixtures for common setup

Example:
```python
import pytest
from src.pipeline.step1_question_generation import generate_questions

def test_generate_questions():
    """Test question generation for malware code images."""
    questions = generate_questions("test.png", "Malware Code")
    assert len(questions) > 0
    assert isinstance(questions, list)
```

## Git Commit Messages

Follow these guidelines:
- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit first line to 72 characters
- Reference issues and PRs when relevant

Examples:
```
Add question generation for new image type

Fix issue #123: Handle empty answer responses

Update README with installation instructions
```

## Project Structure

When adding new features:
- Core pipeline logic goes in `src/pipeline/`
- Utilities go in `src/utils/`
- Tests go in `tests/`
- Documentation goes in `docs/`

## Release Process

1. Update version in `setup.py`
2. Update CHANGELOG.md
3. Create release branch
4. Tag release
5. Update documentation

## Questions?

Feel free to open an issue for any questions or clarifications needed.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
