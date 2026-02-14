from app.db import db
from app.models.user import User
from app.models.provider_profile import ProviderProfile
from app.models.service import Service
from app.models.service_category import ServiceCategory

def test_customer_can_open_favourites_and_notifications(client, app):
    with app.app_context():
        prov = User(email="provf@example.com", role="provider")
        prov.set_password("Passw0rd123")
        cust = User(email="custf@example.com", role="customer")
        cust.set_password("Passw0rd123")
        db.session.add(prov)
        db.session.add(cust)
        db.session.commit()

        db.session.add(ProviderProfile(provider_id=prov.id, is_verified=True))
        db.session.commit()

        category = ServiceCategory(name="Something")
        db.session.add(category)
        db.session.commit()

        s = Service(provider_id=prov.id, category_id=category.id, title="Air conditioners", price=200, location="Sofia")
        db.session.add(s)
        db.session.commit()
        service_id = s.id

    client.post("/login", data={"email": "custf@example.com", "password": "Passw0rd123"}, follow_redirects=True)

    client.post(f"/favourites/{service_id}/add", follow_redirects=True)

    fav = client.get("/favourites", follow_redirects=True)
    assert fav.status_code == 200

    notif = client.get("/notifications", follow_redirects=True)
    assert notif.status_code == 200