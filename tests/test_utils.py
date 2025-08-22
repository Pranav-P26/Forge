import pytest


def test_response_utilities():
    from app.utils.response import success_response, error_response
    
    # Test success response with data and message
    resp, code = success_response(data={"test": "data"}, message="Success")
    assert code == 200
    assert resp.get_json()["success"] is True
    assert resp.get_json()["data"]["test"] == "data"
    assert resp.get_json()["message"] == "Success"
    
    # Test success response defaults (no message)
    resp, code = success_response()
    assert code == 200
    assert resp.get_json()["success"] is True
    assert "message" not in resp.get_json()  # No message when not provided
    
    # Test error response
    resp, code = error_response("TestError", "Test message", 400)
    assert code == 400
    assert resp.get_json()["success"] is False
    assert resp.get_json()["error"] == "TestError"


def test_security_utilities():
    from app.utils.security import hash_password, check_password
    
    password = "test_password_123"
    hashed = hash_password(password)
    
    assert hashed is not None
    assert hashed != password
    assert check_password(hashed, password) is True
    assert check_password(hashed, "wrong_password") is False


def test_validator_utilities():
    from app.utils.validators import require_fields
    
    # Test success case
    data = {"username": "test", "email": "test@example.com"}
    error = require_fields(data, ["username", "email"])
    assert error is None
    
    # Test missing single field
    error = require_fields(data, ["username", "password"])
    assert error is not None
    resp, code = error
    assert code == 400
    assert "password" in resp.get_json()["message"]
    
    # Test missing multiple fields
    error = require_fields({}, ["username", "email", "password"])
    assert error is not None
    resp, code = error
    assert code == 400
    assert "username" in resp.get_json()["message"]
    
    # Test empty data (empty dict, not None)
    error = require_fields({}, ["username"])
    assert error is not None
