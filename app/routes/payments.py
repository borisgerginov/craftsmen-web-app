from flask import Blueprint, redirect, url_for, flash
from flask_login import login_required, current_user
from app.db import db
from app.models.booking import Booking
from app.models.payment import Payment
from app.notifications.notify import notify

payments_bp = Blueprint("payments", __name__)

@payments_bp.route("/my-bookings/<int:booking_id>/pay", methods=["POST"])
@login_required
def pay_booking(booking_id: int):
    if current_user.role != "customer":
        flash("Само клиенти могат да плащат.")
        return redirect(url_for("main.home"))

    b = Booking.query.get_or_404(booking_id)
    if b.customer_id != current_user.id:
        flash("Нямаш права.")
        return redirect(url_for("bookings.my_bookings"))

    if b.status not in ["accepted", "completed"]:
        flash("Можеш да платиш само за приета/завършена резервация.")
        return redirect(url_for("bookings.my_bookings"))

    p = Payment.query.filter_by(booking_id=b.id).first()
    if not p:
        amount = float(b.service.price) if b.service and b.service.price else 0.0
        p = Payment(booking_id=b.id, amount=amount, status="pending")
        db.session.add(p)
        db.session.commit()

    if p.status == "paid":
        flash("Вече е платено.")
        return redirect(url_for("bookings.my_bookings"))

    p.status = "paid"
    db.session.commit()

    flash("Плащането е отбелязано като успешно ✅")
    notify(b.provider_id, f"Клиентът плати за booking #{b.id} 💰")
    return redirect(url_for("bookings.my_bookings"))
