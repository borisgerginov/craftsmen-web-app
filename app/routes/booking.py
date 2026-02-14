from datetime import datetime
from flask import Blueprint, render_template, request, url_for, redirect, flash
from flask_login import login_required, current_user
from app.db import db
from app.models.booking import Booking
from app.models.service import Service
from app.models.provider_profile import ProviderProfile
from app.notifications.notify import notify

bookings_bp = Blueprint("bookings", __name__)

@bookings_bp.route("/services/<int:service_id>/book", methods=["GET", "POST"])
@login_required
def create_booking(service_id: int):
    if current_user.role != "customer":
        flash("Само клиенти могат да правят заявки.")
        return redirect(url_for("main.home"))
    
    service = Service.query.get_or_404(service_id)

    pp = ProviderProfile.query.filter_by(provider_id=service.provider_id).first()
    if not pp or not pp.is_verified:
        flash("Този майстор още не е одобрен.")
        return redirect(url_for("search.search"))
    
    if request.method == "POST":
        scheduled_at_raw = (request.form.get("scheduled_at") or "").strip()
        notes = (request.form.get("notes") or "").strip()

        if not scheduled_at_raw:
            flash("Избери дата и час.")
            return redirect(url_for("bookings.create_booking, service_id=service_id"))
        
        try:
            scheduled_at = datetime.strptime(scheduled_at_raw, "%Y-%m-%dT%H:%M")
        except ValueError:
            flash("Невалиден формат за дата/час.")

        b = Booking(
            customer_id = current_user.id,
            provider_id=service.provider_id,
            service_id=service.id,
            scheduled_at=scheduled_at,
            notes=notes if notes else None,
            status="pending"
        )

        db.session.add(b)
        db.session.commit()

        flash("Заявката е изпратена ✅")
        notify(service.provider_id, f"Нова заявка за услуга '{service.title}' (booking #{b.id}).")

        return redirect(url_for("bookings.my_bookings"))
    
    return render_template("bookings/create.html", service=service)


@bookings_bp.route("/my-bookings", methods=["GET"])
@login_required
def my_bookings():
    if current_user.role == "customer":
        items = (Booking.query.filter_by(customer_id=current_user.id).order_by(Booking.id.desc()).all())
        return render_template("bookings/my_bookings.html", items=items)

    if current_user.role == "provider":
        return render_template("bookings/provider_hub.html")

    flash("Нямаш достъп до тази страница.")
    return redirect(url_for("main.home"))


@bookings_bp.route("/my-bookings/<int:booking_id>/cancel", methods=["POST"])
@login_required
def cancel_booking(booking_id: int):
    if current_user.role != "customer":
        flash("Само клиенти могат да отменят.")
        return redirect(url_for("main.home"))

    b = Booking.query.get_or_404(booking_id)
    if b.customer_id != current_user.id:
        flash("Нямаш права.")
        return redirect(url_for("bookings.my_bookings"))

    if b.status not in ["pending", "accepted"]:
        flash("Тази заявка не може да се отменя.")
        return redirect(url_for("bookings.my_bookings"))

    b.status = "cancelled"
    db.session.commit()
    flash("Отменено.")
    return redirect(url_for("bookings.my_bookings"))