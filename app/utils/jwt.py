from flask_jwt_extended import create_access_token, create_refresh_token

def generate_tokens(user):
    return {
        "access_token": create_access_token(identity=str(user.id)),
        "refresh_token": create_refresh_token(identity=str(user.id))
    }
