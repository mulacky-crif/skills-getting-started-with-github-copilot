"""
Pytest configuration and shared fixtures for the Mergington High School Activities API tests.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture(scope="session")
def test_app():
    """Create a test application instance."""
    return app


@pytest.fixture
def test_client(test_app):
    """Create a test client for the FastAPI application."""
    with TestClient(test_app) as client:
        yield client