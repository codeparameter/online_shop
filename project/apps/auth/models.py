"""User model for authentication"""

from project.config.extensions import db
from datetime import datetime
from helpers.model import Status


class UserRole(Status):
    BUYER = "buyer"
    SELLER = "seller"
    ADMIN = "admin"


class UserStatus(Status):
    ACTIVE = "active"
    VERIFYING = "verifying"
    SUSPENDED = "suspended"


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=UserRole.BUYER.value)
    status = db.Column(db.String(20), nullable=False)
    balance = db.Column(db.Float, nullable=False, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship with products
    products = db.relationship(
        "Product", backref="owner", lazy=True, cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
        }


class TokenBlacklist(db.Model):
    __tablename__ = "token_blacklist"

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, unique=True, index=True)  # JWT ID
    token_type = db.Column(db.String(10), nullable=False)  # 'access' or 'refresh'
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    revoked_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"<TokenBlacklist {self.jti}>"

    @staticmethod
    def is_token_revoked(jti):
        token = TokenBlacklist.query.filter_by(jti=jti).first()
        return token is not None

    @staticmethod
    def add_token_to_blacklist(jti, token_type, user_id, expires_at):
        blacklisted_token = TokenBlacklist(
            jti=jti, token_type=token_type, user_id=user_id, expires_at=expires_at
        )
        db.session.add(blacklisted_token)
        db.session.commit()

    @staticmethod
    def cleanup_expired_tokens():
        TokenBlacklist.query.filter(
            TokenBlacklist.expires_at < datetime.utcnow()
        ).delete()
        db.session.commit()
