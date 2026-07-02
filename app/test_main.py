import sys
from unittest.mock import MagicMock

# 1. Mock the entire redis module BEFORE importing the app
# This prevents the app from trying to open a real network socket during testing
mock_redis_module = MagicMock()
sys.modules['redis'] = mock_redis_module

# 2. Setup mock behavior for the Redis client instances
mock_client = MagicMock()
mock_redis_module.Redis.return_value = mock_client

# Simulate standard Redis responses if your API routes call them
mock_client.get.return_value = None
mock_client.set.return_value = True

# 3. Now safely import the FastAPI TestClient and app
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    """Verify that the base health check endpoint is reachable."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "Online"
