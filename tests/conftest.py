"""
Pytest configuration and fixtures for IRIS testing
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from src.api.server import create_app
from src.core.iris import IRISCore

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def test_app():
    """Create a test instance of the IRIS application."""
    app = create_app()
    return app

@pytest.fixture
def client(test_app):
    """Create a test client for the IRIS application."""
    with TestClient(test_app) as test_client:
        yield test_client

@pytest.fixture
async def iris_core():
    """Create a test instance of IRIS Core."""
    core = IRISCore()
    await core.initialize()
    return core

@pytest.fixture
def sample_user_message():
    """Sample user message for testing."""
    return {
        "message": "Hello IRIS, how are you?",
        "user_id": "test_user_123"
    }
