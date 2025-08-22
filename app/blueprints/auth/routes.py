from flask import request
from . import auth_bp
from app.extensions import db, jwt, redis_client
from app.utils import hash_password, check_password, success_response, error_response, generate_tokens, require_fields
from app.models import User
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt
)
from app.extensions import limiter
from datetime import datetime

# Check if token is blacklisted
@jwt.token_in_blocklist_loader
def check_token_revoked(jwt_header, jwt_payload):
    if redis_client is None:
        return False
    jti = jwt_payload["jti"]
    return redis_client.exists(f"blocklist:{jti}")


# Register
@auth_bp.route("/register", methods=["POST"])
# @limiter.limit("5 per minute")
def register_user():
    if not request.is_json:
        return error_response("Content-Type", "Content-Type must be application/json", 400)

    data = request.get_json()

    error = require_fields(data, ["username", "email", "password"])
    if error:
        return error

    if User.query.filter_by(username=data["username"]).first() or User.query.filter_by(email=data["email"]).first():
        return error_response("Already Exists", "Username or email already exists", 409)

    new_user = User(
        username=data["username"],
        email=data["email"],
        password_hash=hash_password(data["password"])
    )

    db.session.add(new_user)
    db.session.commit()

    return success_response(data=new_user.as_dict(), status_code=201)


# Login
@auth_bp.route("/login", methods=["POST"])
# @limiter.limit("5 per minute")
def login_user():
    if not request.is_json:
        return error_response("Content-Type", "Content-Type must be application/json", 400)

    data = request.get_json()

    error = require_fields(data, ["username", "password"])
    if error:
        return error

    user = User.query.filter_by(username=data["username"]).first()
    if not user or not check_password(user.password_hash, data["password"]):
        return error_response("Unauthorized", "Invalid username or password", 401)

    tokens = generate_tokens(user)
    return success_response(data={"user": user.as_dict(), **tokens})


# Refresh Token
@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
# @limiter.limit("30 per minute")
def refresh_access_token():
    user_id = get_jwt_identity()
    new_access = create_access_token(identity=user_id)
    return success_response(data={"access_token": new_access})


# Revoke access w/ logout
@auth_bp.route("/logout", methods=["DELETE"])
@jwt_required(verify_type=False)
# @limiter.limit("10 per minute")
def logout_user():
    jti = get_jwt()["jti"]
    exp = get_jwt()["exp"]
    token_type = get_jwt()["type"]

    ttl = exp - int(datetime.now().timestamp())
    
    # Only set in Redis if Redis is available
    if redis_client is not None:
        redis_client.setex(f"blocklist:{jti}", ttl, "true")

    return success_response(message=f"{token_type.capitalize()} token revoked, logged out")