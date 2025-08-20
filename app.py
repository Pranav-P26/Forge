from flask import Flask, request, jsonify
from extensions import *
from config import *
from utils.security import hash_password, check_password
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
import os
from datetime import datetime

def create_app(config_name=None):
    app = Flask(__name__)
    
    # If no config is passed in, fall back to FLASK_CONFIG
    if config_name is None:
        config_name = os.getenv("FLASK_CONFIG", "DevConfig")

    config_map = {
        "DevConfig": DevConfig,
        "ProdConfig": ProdConfig,
        "TestConfig": TestConfig,
    }

    # Apply config format
    config_object = config_map.get(config_name)
    if config_object:
        app.config.from_object(config_object)
    else:
        raise ValueError(f"Unknown config: {config_name}")

    # Initialize all extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app)
    limiter.init_app(app)

    global redis_client
    redis_client = redis.from_url(app.config["REDIS_URL"], decode_responses = True)

    from models import User

    # Health check route
    @app.route("/ping")
    def ping():
        return {"status": "ok"}
    
    @jwt.token_in_blocklist_loader
    def check_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        return redis_client.exists(f"blocklist:{jti}")
    
    # Register
    @app.route("/auth/register", methods=["POST"])
    def register_user():
        if request.is_json:
            data = request.get_json()
            required_keys = ["username", "email", "password"]
            
            if not all(key in data for key in required_keys):
                return "Missing required fields", 400
            
            if User.query.filter_by(username=data["username"]).first() or User.query.filter_by(email=data["email"]).first():
                return "Username or email already exists", 400
            else:
                hash = hash_password(data["password"])
                new_user = User(
                    username=data["username"],
                    email=data["email"],
                    password_hash=hash
                )

                db.session.add(new_user)
                db.session.commit()

                return new_user.as_dict(), 201
        else:
            return "Content-Type must be json", 400
        
    # Login
    @app.route("/auth/login", methods=["POST"])
    def login_user():
        if request.is_json:
            data = request.get_json()
            required_keys = ["username", "password"]

            if not all(key in data for key in required_keys):
                return "Missing required fields", 400
            
            user = User.query.filter_by(username=data["username"]).first()
            if not user or not check_password(user.password_hash, data["password"]):
                return "Unauthorized access", 401
            else:
                access_token = create_access_token(identity=str(user.id))
                refresh_token = create_refresh_token(identity=str(user.id))
                return jsonify({
                    "access_token": access_token,
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email
                    }
                }), 200
            
    # Refresh Token
    @app.route("/auth/refresh", methods=["POST"])
    @jwt_required(refresh=True)
    def refresh_access_token():
        user_id = get_jwt_identity()
        new_access = create_access_token(identity=user_id)
        return { "access_token": new_access }, 200
    
    # Revoke access w/ logout
    @app.route("/auth/logout", methods=["DELETE"])
    @jwt_required(verify_type=False)
    def logout_user():
        jti = get_jwt()["jti"]
        exp = get_jwt()["exp"]
        token_type = get_jwt()["type"]

        ttl = exp - int(datetime.now().timestamp())

        redis_client.setex(f"blocklist:{jti}", ttl, "true")

        return {"msg": f"{token_type.capitalize()} token revoked, logged out"}, 200
            
    # Verify login token works
    @app.route("/me", methods=["GET"])
    @jwt_required()
    def get_current_user():
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return "User not found", 404
        
        return jsonify(user.as_dict()), 200

    # CRUD sanity check
    @app.route("/users")
    def query_users():
        users = User.query.all()
        return {"users": [u.as_dict() for u in users]}

    return app

if __name__ == "__main__":
    app = create_app()
    app.run()
