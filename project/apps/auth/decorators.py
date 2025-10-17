"""Authorization decorators for role-based and active-based access control"""

from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from project.apps.auth.models import User, UserRole, UserStatus


def role_required(*allowed_roles, active_required=False):
    """Decorator to check if user has required role"""

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)

            if not user:
                return jsonify({"error": "User not found"}), 404

            if user.role not in allowed_roles:
                return jsonify({"error": "Insufficient permissions"}), 403

            if active_required and user.status in UserStatus.filtered_list(
                UserStatus.ACTIVE
            ):
                return (
                    jsonify(
                        {
                            "error": f"Account is not active. account status: {user.status}"
                        }
                    ),
                    403,
                )

            return fn(*args, **kwargs)

        return wrapper

    return decorator


def seller_required(fn, active_required=False):
    """Decorator to check if user is a seller"""
    return role_required(
        UserRole.SELLER, UserRole.ADMIN, active_required=active_required
    )(fn)


def admin_required(fn, active_required=False):
    """Decorator to check if user is an admin"""
    return role_required(UserRole.ADMIN, active_required=active_required)(fn)
