from flask import Flask
from .extensions import db, migrate, jwt, limiter, cors
import redis
from config import *
from app.utils.response import error_response
from app.utils import setup_logging

def create_app(config_name=None):
    app = Flask(__name__)

    # Config selection
    if config_name is None:
        config_name = os.getenv("FLASK_CONFIG", "DevConfig")

    config_map = {
        "DevConfig": DevConfig,
        "ProdConfig": ProdConfig,
        "TestConfig": TestConfig,
    }

    config_object = config_map.get(config_name)
    if config_object:
        app.config.from_object(config_object)
    else:
        raise ValueError(f"Unknown config: {config_name}")

    # Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app)
    limiter.init_app(app)
    
    setup_logging(app)

    # Redis
    from . import extensions
    extensions.redis_client = redis.from_url(
        app.config["REDIS_URL"], decode_responses=True
    )

    # Blueprints
    from .blueprints.auth import auth_bp
    from .blueprints.users import users_bp
    from .blueprints.main import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(main_bp)

    # Error handles
    @app.errorhandler(404)
    def not_found(e):
        return error_response("Not Found", "The requested resource was not found", 404)

    @app.errorhandler(400)
    def bad_request(e):
        return error_response("Bad Request", str(e), 400)

    @app.errorhandler(401)
    def unauthorized(e):
        return error_response("Unauthorized", str(e), 401)

    @app.errorhandler(403)
    def forbidden(e):
        return error_response("Forbidden", str(e), 403)

    @app.errorhandler(404)
    def not_found(e):
        return error_response("Not Found", "The requested resource was not found", 404)

    @app.errorhandler(500)
    def internal_error(e):
        return error_response("Internal Server Error", "Something went wrong", 500)

    return app
