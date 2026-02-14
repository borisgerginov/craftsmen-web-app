from app.db import db

class Favourite(db.Model):
    __tablename__ = "favourites"

    id = db.Column(db.Integer, primary_key=True)

    customer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    service_id = db.Column(db.Integer, db.ForeignKey("services.id"), nullable=False, index=True)

    __table_args__ = (
        db.UniqueConstraint("customer_id", "service_id", name="uq_fav_customer_service"),
    )
