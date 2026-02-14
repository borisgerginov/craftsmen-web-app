from datetime import datetime
from app.db import db

class Service(db.Model):
    __tablename__ = "services"

    id = db.Column(db.Integer, primary_key=True)

    provider_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey("service_categories.id"), nullable=False, index=True)

    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)

    price = db.Column(db.Integer, nullable=True)
    location = db.Column(db.String(120), nullable=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<Service {self.id} {self.title}>"