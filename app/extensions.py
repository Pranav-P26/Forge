from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_argon2 import Argon2 
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redis, os

# Declaring all libraries / extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()
limiter = Limiter(key_func=get_remote_address)
argon2 = Argon2()
redis_client = None