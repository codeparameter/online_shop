"""Application configuration settings"""

import os
from datetime import timedelta


class Config:
    """Base configuration"""

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT
    JWT_SECRET_KEY = os.environ.get(
        "JWT_SECRET_KEY", "your-secret-key-change-in-production"
    )
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']


    # Security
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = "uploads/products"
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


class DevelopmentConfig(Config):
    """Development configuration"""

    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""

    DEBUG = False


class TestingConfig(Config):
    """Testing configuration"""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL_TEST", "sqlite:///app_test.db"
    )
