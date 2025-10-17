import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from project import create_app
from project.apps.auth.models import TokenBlacklist


def cleanup_expired_tokens():
    app = create_app()

    with app.app_context():
        print("Cleaning up expired tokens from blacklist...")
        TokenBlacklist.cleanup_expired_tokens()
        print("✓ Expired tokens cleaned up successfully!")


if __name__ == "__main__":
    cleanup_expired_tokens()
