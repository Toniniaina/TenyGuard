import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """
    Pytest fixture supplying FastAPI TestClient.
    """
    with TestClient(app) as test_client:
        yield test_client
