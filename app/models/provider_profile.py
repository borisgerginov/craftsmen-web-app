from datetime import datetime
from app.db import db

class ProviderProfile(db.Model):
    __tablename__ = "provider_profiles"

    provider_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        primary_key=True
    )

    is_verified = db.Column(db.Boolean, nullable=False, default=False)
    bio = db.Column(db.Text, nullable=True)
    gallery_links = db.Column(db.Text, nullable=False, default="[]")
    certificates = db.Column(db.Text, nullable=True)

    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


