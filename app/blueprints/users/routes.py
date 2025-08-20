from flask import request, jsonify
from . import users_bp
from app.extensions import db
from app.models import User
from flask_jwt_extended import jwt_required, get_jwt_identity

# Get all users
@users_bp.route("/", methods=["GET"])
@jwt_required()
def list_users():
    users = User.query.all()
    return jsonify({"success": True, "data": [u.as_dict() for u in users]}), 200

# Get current user
@users_bp.route("/me", methods=["GET"])
@jwt_required()
def get_me():
    identity = get_jwt_identity()
    user = User.query.get_or_404(identity)
    return jsonify({"success": True, "data": user.as_dict()}), 200

# Get user by id
@users_bp.route("/<int:user_id>", methods=["GET"])
@jwt_required()
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({"success": True, "data": user.as_dict()}), 200

# Delete user
@users_bp.route("/<int:user_id>", methods=["DELETE"])
@jwt_required()
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"success": True, "message": "User deleted"}), 200
