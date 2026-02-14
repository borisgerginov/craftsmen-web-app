from __future__ import annotations
from datetime import datetime
from flask_login import UserMixin
from enum import Enum

from werkzeug.security import generate_password_hash, check_password_hash
from app.db import db


class UserRole(str, Enum):
    CUSTOMER = "customer"
    PROVIDER = "provider"
    ADMIN = "admin"


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(32), unique=True, nullable=True)

    password_hash = db.Column(db.String(255), nullable=False)

    role = db.Column(
        db.String(20),
        nullable=False,
        default=UserRole.CUSTOMER.value,
        index=True
    )

    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def set_password(self, raw_password: str) -> None:
        if not raw_password or len(raw_password) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> None:
        if not raw_password:
            return False
        return check_password_hash(self.password_hash, raw_password)
    

    def has_role(self, *roles: str) -> bool:
        return self.role in roles
    

    @property
    def is_customer(self) -> bool:
        return self.role == UserRole.CUSTOMER.value
    
    @property
    def is_provider(self) -> bool:
        return self.role == UserRole.PROVIDER.value
    
    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN.value
    

    profile = db.relationship("Profile", uselist=False)
    provider_profile = db.relationship("ProviderProfile", uselist=False)