from app.db import db
from app.models.user import User
from app.models.service import Service
from app.models.service_category import ServiceCategory
from app.models.favourite import Favourite

def test_favourite_model(app):
    with app.app_context():
        customer = User(email="fav@c.com", role="customer")
        customer.set_password("Pass12345")
        provider = User(email="fav@p.com", role="provider")
        provider.set_password("Pass12345")
        db.session.add(customer)
        db.session.add(provider)
        db.session.commit()

        category = ServiceCategory(name="Something")
        db.session.add(category)
        db.session.commit()

        s = Service(provider_id=provider.id, category_id=category.id, title = "Something adorable", price=100, location="Burgas")
        db.session.add(s)
        db.session.commit()

        f = Favourite(customer_id=customer.id, service_id=s.id)
        db.session.add(f)
        db.session.commit()

        assert f.id is not None
        assert f.customer_id == customer.id
        assert f.service_id == s.id