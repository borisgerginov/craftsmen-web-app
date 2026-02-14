from app.db import db
from app.models.user import User
from app.models.provider_profile import ProviderProfile
from app.models.service import Service
from app.models.service_category import ServiceCategory

def test_verified_provider_can_create_service(client, app):
    with app.app_context():
        prov = User(email="prov@example.com", role="provider")
        prov.set_password("Passw0rd123")
        db.session.add(prov)
        db.session.commit()

        pp = ProviderProfile(provider_id=prov.id, is_verified=True)
        db.session.add(pp)
        db.session.commit()

        category = ServiceCategory(name="Something")
        db.session.add(category)
        db.session.commit()

        category_id = category.id

    client.post("/login", data={"email": "prov@example.com", "password": "Passw0rd123"}, follow_redirects=True)

    r = client.get("/provider/services/new")
    assert r.status_code == 200

    r2 = client.post("/provider/services/new", data={
        "title": "Fix door",
        "description": "Door repair",
        "price": "80",
        "location": "Sofia",
        "category_id": str(category_id)},
        follow_redirects=True)
    assert r2.status_code == 200

    with app.app_context():
        s = Service.query.filter_by(title="Fix door").first()
        assert s is not None