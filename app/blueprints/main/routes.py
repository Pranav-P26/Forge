from app.utils import success_response
from . import main_bp

# Welcome message
@main_bp.route("/", methods=["GET"])
def home():
    return success_response(
        data={"version": "1.0.0"},
        message="Welcome to FORGE API"
    )

# Health check
@main_bp.route("/ping", methods=["GET"])
def ping():
    return success_response(message="pong")
