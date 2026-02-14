from app.db import db
from app.models.notification import Notification

def notify(user_id: int, message: str) -> None:
    n = Notification(user_id=user_id, message=message, is_read=False)
    db.session.add(n)
    db.session.commit()