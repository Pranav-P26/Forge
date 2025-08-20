from flask import jsonify
from . import main_bp

# Welcome message
@main_bp.route("/", methods=["GET"])
def home():
    return jsonify({
        "success": True,
        "message": "Welcome to FORGE API",
        "version": "1.0.0"
    }), 200

# Health check
@main_bp.route("/ping", methods=["GET"])
def ping():
    return jsonify({"success": True, "message": "pong"}), 200