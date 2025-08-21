from .response import error_response

def require_fields(data, fields):
    missing = [f for f in fields if f not in data]
    if missing:
        return error_response("Missing Data", f"Missing fields: {', '.join(missing)}", 400)
    return None