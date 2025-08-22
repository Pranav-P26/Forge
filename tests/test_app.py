import pytest
from app import create_app


def test_main_endpoints(client):
    # Test ping endpoint
    response = client.get("/ping")
    data = response.get_json()
    assert response.status_code == 200
    assert data["success"] is True
    assert data["message"] == "pong"
    
    # Test home endpoint
    response = client.get("/")
    data = response.get_json()
    assert response.status_code == 200
    assert data["success"] is True
    assert data["message"] == "Welcome to FORGE API"


def test_error_handlers(client):
    # Test 404 error handler
    resp = client.get("/nonexistent-endpoint")
    assert resp.status_code == 404
    data = resp.get_json()
    assert data["success"] is False
    assert data["error"] == "Not Found"
    
    # Test 400 error handler (bad request)
    resp = client.post("/auth/register", json={})
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["success"] is False
    
    # Test 401 error handler (unauthorized)
    resp = client.get("/users/me")  # No auth header
    assert resp.status_code == 401


def test_app_configuration():
    # Test with test config
    app = create_app("TestConfig")
    assert app.config.get("TESTING") is True
    assert app.config.get("SECRET_KEY") == "test-secret"
    
    # Test with default config (DevConfig)
    app = create_app()
    assert app is not None


def test_model_functionality(db):
    from app.models import User
    
    user = User(
        username="testuser_model",
        email="model@test.com",
        password_hash="test_hash"
    )
    
    # Test the as_dict method
    user_dict = user.as_dict()
    assert user_dict["username"] == "testuser_model"
    assert user_dict["email"] == "model@test.com"
    assert "password_hash" not in user_dict
    assert "created_at" in user_dict
