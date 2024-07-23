import os
import logging

from flask import Flask

from werkzeug.middleware.proxy_fix import ProxyFix
from flask_restful import Api
from flask_cors import CORS

from velero_ui.user import create_admin_user_if_not_exists
from velero_ui.kube_api import auth

from velero_ui.routes import configure_routes

api_version = "v0.4.1"

def create_app():
    use_auth = not (os.getenv("DISABLE_AUTH", "").lower() == "true")
    app = Flask(__name__, static_folder="static")
    app.wsgi_app = ProxyFix(app.wsgi_app, x_prefix=1)
    app.template_folder = "templates"
    app.secret_key = "secret_key"
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    CORS(app)
    api = Api(app)

    # Configure logging

    flask_logger = app.logger
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    if not flask_logger.handlers:
        # If no handlers exist, add a default stream handler
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)
        flask_logger.addHandler(stream_handler)
    else:
        # If there are existing handlers, update their format
        for handler in flask_logger.handlers:
            handler.setFormatter(formatter)
            handler.setLevel(logging.DEBUG)  # Set the desired log level
    
    # Configure routing
    configure_routes(app, api, api_version, use_auth)

    # Authenticate Velero UI client toward Velero server
    auth()

    # Call this function at startup to ensure the admin user exists
    create_admin_user_if_not_exists()

    return app, api
