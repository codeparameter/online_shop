"""Authorization decorators for role-based and active-based access control"""

from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from project.apps.auth.models import User, UserRole, UserStatus


def role_required_validation(role, *allowed_roles):
    return role in allowed_roles


def role_restricted_validation(role, *restricted_roles):
    return role not in restricted_roles


def role_based(is_valid_role, *roles, active_required=False):

    def decorator(fn):
        @jwt_required()
        @wraps(fn)
        def wrapper(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)

            if not user:
                return jsonify({"error": "User not found"}), 404

            if is_valid_role(user.role, *roles):
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


def role_required(*allowed_roles, active_required=False):
    return role_based(
        role_required_validation, *allowed_roles, active_required=active_required
    )


def role_restricted(*restricted_roles, active_required=False):
    return role_based(
        role_restricted_validation, *restricted_roles, active_required=active_required
    )


def seller_required(fn, active_required=False):
    """Decorator to check if user is a seller"""
    return user_required(UserRole.SELLER, active_required=active_required)(fn)


def admin_required(fn, active_required=False):
    """Decorator to check if user is an admin"""
    return user_required(UserRole.ADMIN, active_required=active_required)(fn)
