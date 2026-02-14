from datetime import datetime
from app.db import db
from app.models.user import User
from app.models.service import Service
from app.models.service_category import ServiceCategory
from app.models.booking import Booking
from app.models.payment import Payment

def test_create_payment(app):
    with app.app_context():
        customer = User(email="pay@c.com", role="customer")
        customer.set_password("Pass12345")
        provider = User(email="pay@p.com", role="provider")
        provider.set_password("Pass12345")
        db.session.add(customer)
        db.session.add(provider)
        db.session.commit()

        category = ServiceCategory(name="Something")
        db.session.add(category)
        db.session.commit()

        s = Service(provider_id=provider.id, category_id=category.id, title = "Something to repair", price=70, location="Sofia")
        db.session.add(s)
        db.session.commit()

        b = Booking(customer_id=customer.id, provider_id=provider.id, service_id=s.id, status="accepted", scheduled_at=datetime.utcnow())
        db.session.add(b)
        db.session.commit()

        p = Payment(booking_id=b.id, amount=70, status="paid")
        db.session.add(p)
        db.session.commit()

        assert p.id is not None
        assert p.booking_id == b.id
        assert p.status == "paid"