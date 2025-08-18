from flask import Flask
from extensions import *
from config import *
import os

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

    # Health check route
    @app.route("/ping")
    def ping():
        return {"status": "ok"}

    return app

if __name__ == "__main__":
    app = create_app()
    app.run()
