from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    """Verify that the base health check endpoint returns 200 Online."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "Online"
