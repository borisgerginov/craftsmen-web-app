from app.db import db
from app.models.user import User
from app.models.provider_profile import ProviderProfile
from flask import url_for

def test_customer_apply_for_provider(client, app):
    email = "cust_apply@example.com"
    password = "Pass12345"

    client.post("/register", data={"email": email, "password": password}, follow_redirects=True)
    client.post("/login", data={"email": email, "password": password}, follow_redirects=True)

    r = client.get("/provider/apply", follow_redirects=True)
    assert r.status_code == 200

    r = client.post(
        "/provider/apply",
        data={
            "bio": "5 years experience",
            "gallery_links": "https://img1\nhttps://img2",
            "certificates": "Certificate A (2024)",
        },
        follow_redirects=True,
    )
    assert r.status_code == 200

    with app.app_context():
        u = User.query.filter_by(email=email).first()
        assert u is not None
        pp = ProviderProfile.query.filter_by(provider_id=u.id).first()
        assert pp is not None
        assert pp.is_verified is False

def test_admin_can_approve_provider(client, app):
    with app.app_context():
        u = User(email="pending@example.com", role="customer")
        u.set_password("Pass12345")
        db.session.add(u)
        db.session.commit()
        pp = ProviderProfile(provider_id=u.id, is_verified=False, bio="pending")
        db.session.add(pp)
        db.session.commit()

        admin = User(email="admin@example.com", role="admin")
        admin.set_password("Passw0rd123")
        db.session.add(admin)
        db.session.commit()

        provider_id = u.id
    
    with app.test_request_context():
        pending_url = url_for("admin.pending_providers")
        approve_url = url_for("admin.approve_provider", provider_id=provider_id)

    client.post("/login", data={"email": "admin@example.com", "password": "Passw0rd123"}, follow_redirects=True)

    p = client.get(pending_url, follow_redirects=True)
    assert p.status_code == 200

    a = client.post(approve_url, follow_redirects=True)
    assert a.status_code == 200

    with app.app_context():
        pp2 = ProviderProfile.query.filter_by(provider_id=provider_id).first()
        assert pp2 is not None
        assert pp2.is_verified is True