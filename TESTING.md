# Testing Guide

## Running Tests

### Run All Tests
```bash
# Using pytest directly
pytest tests/ -v

# Using test runner script
./scripts/run_tests.sh
```

### Run Specific Test Categories
```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# Run by marker
pytest -m unit -v
pytest -m integration -v
```

### Run With Coverage
```bash
pytest tests/ --cov=backend --cov-report=html

# View coverage report
open htmlcov/index.html
```

## Code Quality Checks

### Run All Quality Checks
```bash
./scripts/quality_check.sh
```

### Individual Checks

**Format Code with Black:**
```bash
# Check formatting
black --check backend scripts frontend

# Auto-format
black backend scripts frontend
```

**Lint with Flake8:**
```bash
flake8 backend --max-line-length=127 --statistics
```

**Type Check with mypy:**
```bash
mypy backend --ignore-missing-imports
```

**Security Check with Bandit:**
```bash
pip install bandit
bandit -r backend -ll
```

## Test Structure
```
tests/
├── __init__.py
├── unit/                 # Unit tests
│   ├── test_chunker.py
│   ├── test_vector_store.py
│   └── test_query_constructor.py
├── integration/          # Integration tests
│   ├── test_rag_pipeline.py
│   └── test_api.py
└── fixtures/            # Test data
```

## Writing Tests

### Unit Test Example
```python
def test_feature():
    """Test specific feature."""
    # Arrange
    input_data = "test"
    
    # Act
    result = process(input_data)
    
    # Assert
    assert result == expected
```

### Integration Test Example
```python
@pytest.fixture
def setup_system():
    """Setup test system."""
    # Setup code
    return system

def test_integration(setup_system):
    """Test full workflow."""
    system = setup_system
    result = system.process()
    assert result is not None
```

## Continuous Integration

Tests run automatically on:
- Every push to main/develop
- Every pull request
- Using GitHub Actions (`.github/workflows/tests.yml`)

## Coverage Goals

- **Target**: >80% code coverage
- **Critical paths**: 100% coverage
- View reports: `htmlcov/index.html`

## Common Issues

### ImportError
```bash
# Make sure you're in project root
cd /path/to/codebase-rag
export PYTHONPATH=$PWD
pytest tests/
```

### API Tests Failing
```bash
# Start API server first
python scripts/run_api.py

# Then run tests in another terminal
pytest tests/integration/test_api.py
```

### Slow Tests
```bash
# Skip slow tests
pytest tests/ -m "not slow"
```

## Test Coverage Report

Generate detailed coverage:
```bash
pytest tests/ --cov=backend --cov-report=html --cov-report=term-missing

# Coverage summary shown in terminal
# Detailed report: htmlcov/index.html
```

## Pre-commit Checks

Before committing:
```bash
# 1. Format code
black backend scripts frontend

# 2. Run quality checks
./scripts/quality_check.sh

# 3. Run tests
./scripts/run_tests.sh

# 4. Commit if all pass
git commit -m "Your message"
```
