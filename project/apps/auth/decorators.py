"""Authorization decorators for role-based access control"""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from project.apps.auth.models import User, UserRole

def role_required(*allowed_roles):
    """Decorator to check if user has required role"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            if user.role not in allowed_roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def seller_required(fn):
    """Decorator to check if user is a seller"""
    return role_required(UserRole.SELLER, UserRole.ADMIN)(fn)

def admin_required(fn):
    """Decorator to check if user is an admin"""
    return role_required(UserRole.ADMIN)(fn)
