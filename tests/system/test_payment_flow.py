from app.db import db
from flask import url_for
from app.models.user import User
from app.models.provider_profile import ProviderProfile
from app.models.service import Service
from app.models.service_category import ServiceCategory
from app.models.booking import Booking
from app.models.payment import Payment
from datetime import datetime

def test_customer_can_pay_booking(client, app):
    with app.app_context():
        prov = User(email="provpay@example.com", role="provider")
        prov.set_password("Passw0rd123")
        cust = User(email="custpay@example.com", role="customer")
        cust.set_password("Passw0rd123")
        db.session.add(prov)
        db.session.add(cust)
        db.session.commit()

        db.session.add(ProviderProfile(provider_id=prov.id, is_verified=True))
        db.session.commit()

        category = ServiceCategory(name="Something")
        db.session.add(category)
        db.session.commit()

        s = Service(provider_id=prov.id, category_id=category.id, title="Electrician", price=99, location="Sofia")
        db.session.add(s)
        db.session.commit()

        bk = Booking(customer_id=cust.id, provider_id=prov.id, service_id=s.id,
                     status="accepted", scheduled_at=datetime.utcnow())
        db.session.add(bk)
        db.session.commit()
        booking_id = bk.id

    client.post("/login", data={"email": "custpay@example.com", "password": "Passw0rd123"}, follow_redirects=True)

    with app.test_request_context():
        pay_url = url_for("payments.pay_booking", booking_id=booking_id)

    r = client.post(pay_url, follow_redirects=True)
    assert r.status_code == 200

    with app.app_context():
        p = Payment.query.filter_by(booking_id=booking_id).first()
        assert p is not None
        assert p.status in ("paid", "success")
