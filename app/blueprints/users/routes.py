from . import users_bp
from app.extensions import db
from app.models import User
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils import success_response, error_response
from app.extensions import limiter

# Get all users
@users_bp.route("/", methods=["GET"])
@jwt_required()
@limiter.limit("20 per minute")
def list_users():
    users = User.query.all()
    return success_response(data=[u.as_dict() for u in users])

# Get current user
@users_bp.route("/me", methods=["GET"])
@jwt_required()
@limiter.limit("60 per minute")
def get_me():
    identity = get_jwt_identity()
    user = User.query.get(identity)

    if not user:
        return error_response("Not Found", "User not found", 404)
    
    return success_response(data=user.as_dict())

# Get user by id
@users_bp.route("/<int:user_id>", methods=["GET"])
@jwt_required()
@limiter.limit("30 per minute")
def get_user(user_id):
    user = User.query.get(user_id)

    if not user:
        return error_response("Not Found", f"User with id {user_id} not found", 404)
    
    return success_response(data=user.as_dict())

# Delete user
@users_bp.route("/<int:user_id>", methods=["DELETE"])
@jwt_required()
@limiter.limit("5 per minute")
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return error_response("Not Found", f"User with id {user_id} not found", 404)
    
    db.session.delete(user)
    db.session.commit()

    return success_response(message="User deleted")
