from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.db import db
from app.models.booking import Booking
from app.models.provider_profile import ProviderProfile
from app.notifications.notify import notify

provider_bookings_bp = Blueprint("provider_bookings", __name__)

def deny_if_not_verified_provider():
    if current_user.role != "provider":
        flash("Само майстори имат достъп.")
        return(redirect(url_for("main.home")))
    
    pp = ProviderProfile.query.filter_by(provider_id=current_user.id).first()
    if not pp or not pp.is_verified:
        flash("Профилът ти още не е одобрен.")
        return redirect(url_for("provider.status"))

    return None


@provider_bookings_bp.route("/provider/bookings/incoming", methods=["GET"])
@login_required
def incoming():
    deny = deny_if_not_verified_provider()
    if deny:
        return deny
    
    items = (Booking.query.filter_by(provider_id=current_user.id, status="pending").order_by(Booking.id.desc()).all())

    return render_template("provider/bookings_incoming.html", items=items)


@provider_bookings_bp.route("/provider/bookings/schedule", methods=["GET"])
@login_required
def schedule():
    deny = deny_if_not_verified_provider()
    if deny:
        return deny

    items = (Booking.query
             .filter_by(provider_id=current_user.id, status="accepted")
             .order_by(Booking.scheduled_at.asc())
             .all())

    return render_template("provider/bookings_schedule.html", items=items)


@provider_bookings_bp.route("/provider/bookings/<int:booking_id>/accept", methods=["POST"])
@login_required
def accept(booking_id: int):
    deny = deny_if_not_verified_provider()
    if deny:
        return deny
    
    b = Booking.query.get_or_404(booking_id)
    if b.provider_id != current_user.id:
        flash("Нямаш права.")
        return redirect(url_for("provider_bookings.incoming"))
    
    if b.status != "pending":
        flash("Тази заявка не е pending.")
        return redirect(url_for("provider_bookings.incoming"))
    
    b.status = "accepted"
    db.session.commit()
    flash("Прието ✅")
    notify(b.customer_id, f"Заявката ти (booking #{b.id}) беше приета ✅")
    return redirect(url_for("provider_bookings.incoming"))

@provider_bookings_bp.route("/provider/bookings/<int:booking_id>/reject", methods=["POST"])
@login_required
def reject(booking_id: int):
    deny = deny_if_not_verified_provider()
    if deny:
        return deny

    b = Booking.query.get_or_404(booking_id)
    if b.provider_id != current_user.id:
        flash("Нямаш права.")
        return redirect(url_for("provider_bookings.incoming"))

    if b.status != "pending":
        flash("Тази заявка не е pending.")
        return redirect(url_for("provider_bookings.incoming"))

    b.status = "rejected"
    db.session.commit()
    flash("Отказано.")
    notify(b.customer_id, f"Заявката ти (booking #{b.id}) беше отхвърлена ❌")
    return redirect(url_for("provider_bookings.incoming"))


@provider_bookings_bp.route("/provider/bookings/<int:booking_id>/complete", methods=["POST"])
@login_required
def complete(booking_id: int):
    deny = deny_if_not_verified_provider()
    if deny:
        return deny
    
    b = Booking.query.get_or_404(booking_id)
    if b.provider_id != current_user.id:
        flash("Нямаш права.")
        return redirect(url_for("provider_bookings.schedule"))
    
    if b.status != "accepted":
        flash("Само accepted може да стане completed.")
        return redirect(url_for("provider_bookings.schedule"))
    
    b.status = "completed"
    db.session.commit()
    flash("Маркирано като завършено ✅")
    notify(b.customer_id, f"Услугата по booking #{b.id} е маркирана като завършена ✅ Можеш да оставиш ревю.")
    return redirect(url_for("provider_bookings.schedule"))