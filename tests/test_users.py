import pytest
from flask_jwt_extended import create_access_token


def test_get_current_user(client, db, app):
    from app.models import User
    from app.utils import hash_password

    user = User(username="bob", email="bob@example.com", password_hash=hash_password("secret"))
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))

    resp = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["data"]["username"] == "bob"


def test_get_current_user_not_found(client, db, app):
    with app.app_context():
        token = create_access_token(identity="9999")
    
    resp = client.get("/users/me", headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert resp.status_code == 404
    data = resp.get_json()
    assert data["success"] is False


def test_list_users(client, auth_headers, db):
    resp = client.get("/users/", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert isinstance(data["data"], list)


def test_get_user_by_id(client, auth_headers, db):
    from app.models import User
    from app.utils import hash_password
    
    user = User(
        username="getuser",
        email="get@example.com", 
        password_hash=hash_password("secret")
    )
    db.session.add(user)
    db.session.commit()
    
    resp = client.get(f"/users/{user.id}", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["data"]["username"] == "getuser"
    
    # Test non-existent user
    resp = client.get("/users/999", headers=auth_headers)
    assert resp.status_code == 404


def test_delete_user(client, auth_headers, db):
    from app.models import User
    from app.utils import hash_password
    
    user = User(
        username="deleteme",
        email="delete@example.com", 
        password_hash=hash_password("secret")
    )
    db.session.add(user)
    db.session.commit()
    user_id = user.id
    
    # Delete the user
    resp = client.delete(f"/users/{user_id}", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    
    # Try to delete non-existent user
    resp = client.delete("/users/999", headers=auth_headers)
    assert resp.status_code == 404
