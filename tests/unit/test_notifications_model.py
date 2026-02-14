from app.db import db
from app.models.notification import Notification

def test_notifications_models(app):
    with app.app_context():
        n = Notification(user_id=1, message="Hello")
        db.session.add(n)
        db.session.commit()

        assert n.id is not None
        assert n.user_id == 1
        assert n.message == "Hello"