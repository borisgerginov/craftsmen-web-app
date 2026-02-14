from datetime import datetime
from app.db import db
from app.models.user import User
from app.models.service import Service
from app.models.booking import Booking
from app.models.service_category import ServiceCategory

def test_create_booking(app):
    with app.app_context():
        customer = User(email="c@c.com", role="customer")
        customer.set_password("Pass12345")
        provider = User(email="p@p.com", role="provider")
        provider.set_password("Pass12345")

        db.session.add(customer)
        db.session.add(provider)
        db.session.commit()

        category = ServiceCategory(name="Something")
        db.session.add(category)
        db.session.commit()

        s = Service(
            provider_id = provider.id,
            category_id = category.id,
            title = "Fix sink",
            description = "Fixing a sink",
            price = 50,
            location="Sofia"
        )

        db.session.add(s)
        db.session.commit()

        b = Booking(
            customer_id = customer.id,
            provider_id = provider.id,
            service_id = s.id,
            status = "pending",
            scheduled_at=datetime.utcnow()
        )

        db.session.add(b)
        db.session.commit()

        assert b.id is not None
        assert b.status == "pending"
        assert b.customer_id == customer.id