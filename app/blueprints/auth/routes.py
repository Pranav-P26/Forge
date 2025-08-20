from flask import request, jsonify
from . import auth_bp
from app.extensions import db, jwt, redis_client
from app.utils.security import hash_password, check_password
from app.models import User
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from datetime import datetime

# Check if token is blacklisted
@jwt.token_in_blocklist_loader
def check_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    return redis_client.exists(f"blocklist:{jti}")

# Register
@auth_bp.route("/register", methods=["POST"])
def register_user():
    if not request.is_json:
        return jsonify({"success": False, "error": "Content-Type must be application/json"}), 400

    data = request.get_json()
    required_keys = ["username", "email", "password"]

    if not all(key in data for key in required_keys):
        return jsonify({"success": False, "error": "Missing required fields"}), 400

    if User.query.filter_by(username=data["username"]).first() or User.query.filter_by(email=data["email"]).first():
        return jsonify({"success": False, "error": "Username or email already exists"}), 400

    new_user = User(
        username=data["username"],
        email=data["email"],
        password_hash=hash_password(data["password"])
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"success": True, "data": new_user.as_dict()}), 201
    
# Login
@auth_bp.route("/login", methods=["POST"])
def login_user():
    if not request.is_json:
        return jsonify({"success": False, "error": "Content-Type must be application/json"}), 400

    data = request.get_json()
    required_keys = ["username", "password"]

    if not all(key in data for key in required_keys):
        return jsonify({"success": False, "error": "Missing required fields"}), 400

    user = User.query.filter_by(username=data["username"]).first()
    if not user or not check_password(user.password_hash, data["password"]):
        return jsonify({"success": False, "error": "Unauthorized"}), 401

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        "success": True,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": user.as_dict()
    }), 200
        
# Refresh Token
@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh_access_token():
    user_id = get_jwt_identity()
    new_access = create_access_token(identity=user_id)
    return jsonify({"success": True, "access_token": new_access}), 200

# Revoke access w/ logout
@auth_bp.route("/logout", methods=["DELETE"])
@jwt_required(verify_type=False)
def logout_user():
    jti = get_jwt()["jti"]
    exp = get_jwt()["exp"]
    token_type = get_jwt()["type"]

    ttl = exp - int(datetime.now().timestamp())
    redis_client.setex(f"blocklist:{jti}", ttl, "true")

    return jsonify({"success": True, "message": f"{token_type.capitalize()} token revoked, logged out"}), 200