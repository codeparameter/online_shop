"""Authentication views (route handlers)"""

from flask import request, jsonify
from flask_jwt_extended import (
    create_access_token,
    unset_jwt_cookies,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)
from project.config.extensions import db, bcrypt
from project.apps.auth.models import User, UserRole, TokenBlacklist
from project.apps.auth.validators import validate_registration, validate_login
from project.apps.auth.decorators import admin_required
from datetime import datetime


def register():
    """Register a new user"""
    data = request.get_json()

    # Validate input
    is_valid, errors = validate_registration(data)
    if not is_valid:
        return jsonify({"errors": errors}), 400

    # Check if user already exists
    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"error": "Username already exists"}), 409

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already exists"}), 409

    role = data.get("role", UserRole.BUYER)
    allowed_roles = UserRole.get_roles_dict()
    allowed_roles.pop("ADMIN")
    if role not in allowed_roles.values():
        return jsonify({"error": "Invalid role"}), 400

    # Create new user
    hashed_password = bcrypt.generate_password_hash(data["password"]).decode("utf-8")
    new_user = User(
        username=data["username"],
        email=data["email"],
        password_hash=hashed_password,
        role=role,
    )

    try:
        db.session.add(new_user)
        db.session.commit()

        # Create access token
        access_token = create_access_token(identity=new_user.id)

        return (
            jsonify(
                {
                    "message": "User registered successfully",
                    "user": new_user.to_dict(),
                    "access_token": access_token,
                }
            ),
            201,
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to register user"}), 500


def login():
    """Login user"""
    data = request.get_json()

    # Validate input
    is_valid, errors = validate_login(data)
    if not is_valid:
        return jsonify({"errors": errors}), 400

    # Find user
    user = User.query.filter_by(username=data["username"]).first()

    if not user or not bcrypt.check_password_hash(user.password_hash, data["password"]):
        return jsonify({"error": "Invalid username or password"}), 401

    # Create access token
    access_token = create_access_token(identity=str(user.id))

    return (
        jsonify(
            {
                "message": "Login successful",
                "user": user.to_dict(),
                "access_token": access_token,
            }
        ),
        200,
    )


@jwt_required()
def logout():
    """Logout user by blacklisting the token"""
    jwt_data = get_jwt()
    jti = jwt_data["jti"]  # JWT ID
    token_type = jwt_data["type"]  # 'access' or 'refresh'
    user_id = get_jwt_identity()

    exp_timestamp = jwt_data["exp"]
    expires_at = datetime.fromtimestamp(exp_timestamp)

    try:
        TokenBlacklist.add_token_to_blacklist(
            jti=jti, token_type=token_type, user_id=user_id, expires_at=expires_at
        )

        return jsonify({"message": "Logout successful, token has been revoked"}), 200
    except Exception as e:
        print(e)
        return jsonify({"error": "Failed to logout"}), 500


@jwt_required()
def profile():
    """Get user profile"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"user": user.to_dict()}), 200
