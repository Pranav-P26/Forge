from app.extensions import argon2

def hash_password(password):
    return argon2.generate_password_hash(password)

def check_password(hash, candidate):
    try:
        return argon2.check_password_hash(hash, candidate)
    except Exception:
        return False