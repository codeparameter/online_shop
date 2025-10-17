"""Authentication form validators"""

import re
from project.apps.auth.models import UserRole


def validate_email(email):
    """Validate email format"""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def validate_registration(data):
    """Validate user registration data"""
    errors = []

    # Check required fields
    if not data.get("username"):
        errors.append("Username is required")
    elif len(data["username"]) < 3:
        errors.append("Username must be at least 3 characters long")
    elif len(data["username"]) > 80:
        errors.append("Username must be less than 80 characters")

    if not data.get("email"):
        errors.append("Email is required")
    elif not validate_email(data["email"]):
        errors.append("Invalid email format")

    if not data.get("password"):
        errors.append("Password is required")
    elif len(data["password"]) < 6:
        errors.append("Password must be at least 6 characters long")

    if "role" in data and data["role"] not in UserRole.filtered_list():
        errors.append(
            f'Invalid role. Must be one of: {", ".join(UserRole.filtered_list())}'
        )

    return len(errors) == 0, errors


def validate_login(data):
    """Validate login data"""
    errors = []

    if not data.get("username"):
        errors.append("Username is required")

    if not data.get("password"):
        errors.append("Password is required")

    return len(errors) == 0, errors
