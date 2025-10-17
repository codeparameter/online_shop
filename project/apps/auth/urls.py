"""Authentication URL patterns (routes)"""

from flask import Blueprint
from project.apps.auth import views

auth_bp = Blueprint("auth", __name__)

# Register routes
auth_bp.add_url_rule("/register", "register", views.register, methods=["POST"])
auth_bp.add_url_rule("/login", "login", views.login, methods=["POST"])
auth_bp.add_url_rule("/logout", "logout", views.logout, methods=["POST"])
auth_bp.add_url_rule("/profile", "profile", views.profile, methods=["GET"])
auth_bp.add_url_rule(
    "/increase-balance", "increase_balance", views.increase_balance, methods=["POST"]
)
auth_bp.add_url_rule(
    "/user-status", "change_user_status", views.change_user_status, methods=["PUT"]
)
