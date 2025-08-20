from flask import Flask
from .extensions import db, migrate, jwt, limiter, cors
import redis
from config import *

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

    return app
