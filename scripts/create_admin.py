"""Script to create an admin user"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from project import create_app
from project.config.extensions import db, bcrypt
from project.apps.auth.models import User, UserRole

def create_admin_user(username, email, password):
    """Create an admin user"""
    app = create_app()
    
    with app.app_context():
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"User '{username}' already exists!")
            return
        
        # Create admin user
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        admin_user = User(
            username=username,
            email=email,
            password_hash=hashed_password,
            role=UserRole.ADMIN
        )
        
        db.session.add(admin_user)
        db.session.commit()
        
        print(f"Admin user '{username}' created successfully!")
        print(f"Email: {email}")
        print(f"Role: {admin_user.role}")

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python scripts/create_admin.py <username> <email> <password>")
        sys.exit(1)
    
    username = sys.argv[1]
    email = sys.argv[2]
    password = sys.argv[3]
    
    create_admin_user(username, email, password)
