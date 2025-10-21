# Test Suite for Mergington High School Activities API

This directory contains comprehensive tests for the FastAPI application that manages student activity registrations.

## Test Structure

- `test_api.py` - Main test file containing all API endpoint tests
- `conftest.py` - Pytest configuration and shared fixtures
- `__init__.py` - Package initialization

## Test Coverage

The test suite covers:

### API Endpoints
- **GET /activities** - Retrieve all activities
- **POST /activities/{activity_name}/signup** - Register for an activity  
- **DELETE /activities/{activity_name}/unregister** - Unregister from an activity
- **GET /** - Root endpoint redirect

### Test Categories

1. **Unit Tests** - Individual endpoint functionality
2. **Error Handling** - Invalid inputs, missing resources, business rule violations
3. **Integration Tests** - Complete user workflows
4. **Edge Cases** - Boundary conditions (full activities, duplicate registrations)

## Running Tests

### Basic Test Run
```bash
python -m pytest tests/
```

### Verbose Output
```bash
python -m pytest tests/ -v
```

### With Coverage Report
```bash
python -m pytest tests/ --cov=src --cov-report=term-missing
```

### Generate HTML Coverage Report
```bash
python -m pytest tests/ --cov=src --cov-report=html
```

## Test Results

Current test coverage: **100%** ✅

- 16 test cases
- All major functionality covered
- Error conditions tested
- Integration scenarios validated

## Dependencies

The following testing dependencies are required:
- `pytest` - Testing framework
- `pytest-asyncio` - Async test support
- `pytest-cov` - Coverage reporting
- `httpx` - HTTP client for FastAPI testing

All dependencies are listed in `requirements.txt` and can be installed with:
```bash
pip install -r requirements.txt
```