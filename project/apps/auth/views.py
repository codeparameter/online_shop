"""Authentication views (route handlers)"""

from flask import request, jsonify
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    get_jwt,
)
from project.config.extensions import db, bcrypt
from project.apps.auth.models import User, UserRole, UserStatus, TokenBlacklist
from project.apps.auth.validators import validate_registration, validate_login
from project.apps.auth.decorators import admin_required, role_restricted
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

    role = data.get("role", UserRole.BUYER.value)

    if role not in UserRole.filtered_list(UserRole.ADMIN):
        return jsonify({"error": "Invalid role"}), 400

    if role == UserRole.BUYER.value:
        status = UserStatus.ACTIVE.value
    elif role == UserRole.SELLER.value:
        status = UserStatus.VERIFYING.value
    else:
        return jsonify({"error": "Invalid role"}), 400

    # Create new user
    hashed_password = bcrypt.generate_password_hash(data["password"]).decode("utf-8")
    new_user = User(
        username=data["username"],
        email=data["email"],
        password_hash=hashed_password,
        role=role,
        status=status,
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


@role_restricted(active_required=False)
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


@role_restricted(active_required=False)
def profile():
    """Get user profile"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    return jsonify({"user": user.to_dict()}), 200


@role_restricted
def increase_balance():
    """Increase user balance (for testing/admin purposes)"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    data = request.get_json()
    amount = data.get("amount")
    if not amount or amount <= 0:
        return jsonify({"error": "Invalid amount"}), 400
    try:
        user.balance += float(amount)
        db.session.commit()
        return (
            jsonify(
                {
                    "message": "Balance increased successfully",
                    "new_balance": user.balance,
                }
            ),
            200,
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to increase balance"}), 500


@admin_required
def change_user_status():
    """Change user status (admin only)"""
    user_id = request.args.get("user_id", type=int)
    new_status = request.args.get("status")
    if not user_id or not new_status:
        return jsonify({"error": "user_id and status are required"}), 400
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    # Validate status transitions based on role
    valid_transitions = {
        UserRole.BUYER.value: {
            UserStatus.ACTIVE.value: [UserStatus.SUSPENDED.value],
            UserStatus.SUSPENDED.value: [UserStatus.ACTIVE.value],
        },
        UserRole.SELLER.value: {
            UserStatus.VERIFYING.value: [
                UserStatus.ACTIVE.value,
                UserStatus.SUSPENDED.value,
            ],
            UserStatus.ACTIVE.value: [UserStatus.SUSPENDED.value],
            UserStatus.SUSPENDED.value: [UserStatus.ACTIVE.value],
        },
        UserRole.ADMIN.value: {
            UserStatus.ACTIVE.value: [UserStatus.SUSPENDED.value],
            UserStatus.SUSPENDED.value: [UserStatus.ACTIVE.value],
        },
    }
    current_status = user.status
    allowed_statuses = valid_transitions.get(user.role, {}).get(current_status, [])
    if new_status not in allowed_statuses:
        return (
            jsonify(
                {
                    "error": f"Invalid status transition from {current_status} to {new_status} for role {user.role}"
                }
            ),
            400,
        )
    try:
        user.status = new_status
        db.session.commit()
        return (
            jsonify(
                {
                    "message": "User status updated successfully",
                    "user": user.to_dict(include_status=True),
                }
            ),
            200,
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to update user status"}), 500
