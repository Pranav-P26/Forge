import logging
from flask import request

def setup_logging(app):
    # Basic configuration
    logging.basicConfig(
        level = logging.INFO,
        format = "%(asctime)s [%(levelname)s] %(message)s"
    )

    @app.before_request
    def log_request_info():
        logging.info(f"Request: {request.method} {request.path}")

    @app.after_request
    def log_response_info(response):
        logging.info(f"Response: {response.status} {response.get_data(as_text=True)}")
        return response