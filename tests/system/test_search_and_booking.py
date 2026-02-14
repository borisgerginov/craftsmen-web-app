from datetime import datetime, timedelta
from app.db import db
from app.models.user import User
from app.models.provider_profile import ProviderProfile
from app.models.service import Service
from app.models.service_category import ServiceCategory
from app.models.booking import Booking
from flask import url_for

def test_customer_searches_and_books(client, app):
    with app.app_context():
        prov = User(email="prov2@example.com", role="provider")
        prov.set_password("Passw0rd123")
        cust = User(email="cust2@example.com", role="customer")
        cust.set_password("Passw0rd123")
        db.session.add(prov)
        db.session.add(cust)
        db.session.commit()

        db.session.add(ProviderProfile(provider_id=prov.id, is_verified=True))
        db.session.commit()

        category = ServiceCategory(name="Something")
        db.session.add(category)
        db.session.commit()
        category_id = category.id

        s = Service(provider_id=prov.id, category_id=category_id, title="Plumber", price=50, location="Sofia")
        db.session.add(s)
        db.session.commit()
        service_id = s.id

    client.post("/login", data={"email": "cust2@example.com", "password": "Passw0rd123"}, follow_redirects=True)

    r = client.get("/search?q=Plumber", follow_redirects=True)
    assert r.status_code == 200


    b = client.post(f"/services/{service_id}/book", data={"scheduled_at": "2026-04-27T10:00"}, follow_redirects=True)
    assert b.status_code == 200

    with app.app_context():
        bk = Booking.query.filter_by(service_id=service_id).first()
        assert bk is not None