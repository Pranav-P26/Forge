import os

# Common configuration settings shared across all environments
class BaseConfig:
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")

# Configuration specific towards development builds
class DevConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///dev.db")

# Configuration specific towards production builds
class ProdConfig(BaseConfig):
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")

# Configuration specific towards integration tests
class TestConfig(BaseConfig):
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
