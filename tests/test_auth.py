import pytest
from flask_jwt_extended import create_access_token, create_refresh_token


def test_register_and_login(client, db):
    # Register
    resp = client.post("/auth/register", json={
        "username": "alice",
        "email": "alice@example.com",
        "password": "password123"
    })
    assert resp.status_code == 201
    assert resp.get_json()["success"] is True

    # Login
    resp = client.post("/auth/login", json={
        "username": "alice",
        "password": "password123"
    })
    data = resp.get_json()
    assert resp.status_code == 200
    assert "access_token" in data["data"]
    assert "refresh_token" in data["data"]


def test_register_validation_errors(client, db):
    # Test missing fields
    resp = client.post("/auth/register", json={"username": "u"})
    assert resp.status_code == 400
    
    # Test invalid content type
    resp = client.post("/auth/register", data="notjson")
    assert resp.status_code == 400
    
    # Test duplicate user
    client.post("/auth/register", json={
        "username": "duplicate",
        "email": "dup@example.com",
        "password": "password123"
    })
    resp = client.post("/auth/register", json={
        "username": "duplicate",
        "email": "dup2@example.com",
        "password": "password123"
    })
    assert resp.status_code == 409


def test_login_validation_errors(client, db):
    # Test invalid user
    resp = client.post("/auth/login", json={
        "username": "nonexistent",
        "password": "any_password"
    })
    assert resp.status_code == 401
    
    # Test wrong password
    client.post("/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "correct_password"
    })
    resp = client.post("/auth/login", json={
        "username": "testuser",
        "password": "wrong_password"
    })
    assert resp.status_code == 401


def test_refresh_token(client, db):
    # Register and login
    client.post("/auth/register", json={
        "username": "refreshuser",
        "email": "refresh@example.com", 
        "password": "secret"
    })
    
    login_resp = client.post("/auth/login", json={
        "username": "refreshuser",
        "password": "secret"
    })
    
    login_data = login_resp.get_json()
    refresh_token = login_data["data"]["refresh_token"]
    
    # Test refresh
    resp = client.post("/auth/refresh", headers={
        "Authorization": f"Bearer {refresh_token}"
    })
    
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert "access_token" in data["data"]


def test_logout(client, auth_headers):
    resp = client.delete("/auth/logout", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert "token revoked" in data["message"].lower()


def test_token_blocklist_functionality(client, db):
    # Register and login
    client.post("/auth/register", json={
        "username": "blocklistuser",
        "email": "blocklist@example.com",
        "password": "secret"
    })
    
    login_resp = client.post("/auth/login", json={
        "username": "blocklistuser",
        "password": "secret"
    })
    
    login_data = login_resp.get_json()
    access_token = login_data["data"]["access_token"]
    
    # Logout
    resp = client.delete("/auth/logout", headers={
        "Authorization": f"Bearer {access_token}"
    })
    assert resp.status_code == 200
