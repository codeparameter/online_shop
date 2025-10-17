"""Main application factory"""

from flask import Flask, jsonify
from project.config.settings import Config
from project.config.extensions import db, bcrypt, jwt


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    register_jwt_callbacks(app)

    # Register blueprints
    from project.apps.auth.urls import auth_bp
    from project.apps.products.urls import products_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(products_bp, url_prefix="/api/products")

    # Register error handlers
    register_error_handlers(app)

    # Root endpoint
    @app.route("/")
    def index():
        return jsonify(
            {
                "message": "Flask CRUD API",
                "endpoints": {
                    "auth": {
                        "register": "POST /api/auth/register",
                        "login": "POST /api/auth/login",
                        "logout": "POST /api/auth/logout",
                        "profile": "GET /api/auth/profile",
                    },
                    "products": {
                        "create": "POST /api/products",
                        "list": "GET /api/products",
                        "get": "GET /api/products/<id>",
                        "update": "PUT /api/products/<id>",
                        "delete": "DELETE /api/products/<id>",
                    },
                },
            }
        )

    return app


def register_jwt_callbacks(app):
    from project.apps.auth.models import TokenBlacklist

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        return TokenBlacklist.is_token_revoked(jti)

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {"error": "Token has been revoked", "message": "Please login again"}
            ),
            401,
        )


def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal server error"}), 500
