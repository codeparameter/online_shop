import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from project import create_app
from project.config.extensions import db


def create_tables():
    app = create_app()

    with app.app_context():
        # Import all models to ensure they're registered
        from project.apps.auth.models import User, TokenBlacklist
        from project.apps.products.models import Product

        # Create all tables
        db.create_all()
        print("✓ Database tables created successfully!")
        print("  - users")
        print("  - token_blacklist")
        print("  - products")


if __name__ == "__main__":
    create_tables()
