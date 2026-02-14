from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.db import db
from app.models.notification import Notification

notifications_bp = Blueprint("notifications", __name__)

@notifications_bp.route("/notifications", methods=["GET"])
@login_required
def list_notifications():
    items = (Notification.query
             .filter_by(user_id=current_user.id)
             .order_by(Notification.id.desc())
             .all())
    return render_template("notifications/list.html", items=items)

@notifications_bp.route("/notifications/<int:notif_id>/read", methods=["POST"])
@login_required
def mark_read(notif_id: int):
    n = Notification.query.get_or_404(notif_id)
    if n.user_id != current_user.id:
        return redirect(url_for("notifications.list_notifications"))

    n.is_read = True
    db.session.commit()
    return redirect(url_for("notifications.list_notifications"))
