from app.db import db
from app.models.user import User
from app.models.provider_profile import ProviderProfile
from app.models.service import Service
from app.models.service_category import ServiceCategory
from app.models.booking import Booking
from app.models.review import Review
from datetime import datetime
from flask import url_for

def test_customer_can_leave_review(client, app):
    with app.app_context():
        prov = User(email="provr@example.com", role="provider")
        prov.set_password("Passw0rd123")
        cust = User(email="custr@example.com", role="customer")
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

        s = Service(provider_id=prov.id, category_id=category_id, title="Painter", price=120, location="Sofia")
        db.session.add(s)
        db.session.commit()

        bk = Booking(customer_id=cust.id, provider_id=prov.id, service_id=s.id,
                     status="completed", scheduled_at=datetime.utcnow())
        db.session.add(bk)
        db.session.commit()
        booking_id = bk.id

    with app.test_request_context():
        review_url = url_for("reviews.add_review", booking_id=booking_id)

    client.post("/login", data={"email": "custr@example.com", "password": "Passw0rd123"}, follow_redirects=True)

    r = client.post(review_url, data={"rating": "5", "comment": "Great"}, follow_redirects=True)
    assert r.status_code == 200

    with app.app_context():
        rev = Review.query.filter_by(booking_id=booking_id).first()
        assert rev is not None
        assert rev.rating == 5
