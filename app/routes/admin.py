from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.db import db
from app.models.user import User
from app.models.provider_profile import ProviderProfile
from app.notifications.notify import notify
from app.models.service import Service
from app.models.booking import Booking
from app.models.review import Review
from app.models.payment import Payment

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

def _admin_only():
    if current_user.role != "admin":
        flash("Нямаш достъп (admin only).")
        return redirect(url_for("main.home"))
    return None

def deny_if_not_admin():
    if current_user.role != "admin":
        flash("Нямаш права.")
        return redirect(url_for("main.home"))
    return None

@admin_bp.route("/admin/providers/pending", methods=["GET"])
@login_required
def pending_providers():
    deny = deny_if_not_admin()
    if deny:
        return deny
    
    pending = ProviderProfile.query.filter_by(is_verified=False).all()
    return render_template("admin/pending_providers.html", pending=pending)

@admin_bp.route("/admin/providers/<int:provider_id>/approve", methods=["POST"])
@login_required
def approve_provider(provider_id: int):
    deny = deny_if_not_admin()
    if deny:
        return deny
    
    pp = ProviderProfile.query.filter_by(provider_id=provider_id).first()
    if pp is None:
        flash("Не е намерена кандидатура.")
        return redirect(url_for("admin.pending_providers"))
    
    pp.is_verified = True
    user = User.query.get(provider_id)
    if user:
        user.role = "provider"

    db.session.commit()
    flash("Майсторът е одобрен ✅")
    notify(provider_id, "Профилът ти като майстор е одобрен ✅ Вече можеш да приемаш заявки.")
    return redirect(url_for("admin.pending_providers"))

@admin_bp.route("/admin/providers/<int:provider_id>/reject", methods=["POST"])
@login_required
def reject_provider(provider_id: int):
    deny = deny_if_not_admin()
    if deny:
        return deny
    
    pp = ProviderProfile.query.filter_by(provider_id=provider_id).first()
    if pp is None:
        flash("Не е намерена кандидатура.")
        return redirect(url_for("admin.pending_providers"))
    
    db.session.delete(pp)
    db.session.commit()
    flash("Кандидатурата е отхвърлена.")
    return redirect(url_for("admin.pending_providers"))

@admin_bp.route("/", methods=["GET"])
@login_required
def dashboard():
    deny = _admin_only()
    if deny:
        return deny
    return render_template("admin/dashboard.html")


@admin_bp.route("/users", methods=["GET"])
@login_required
def users():
    deny = _admin_only()
    if deny:
        return deny

    items = User.query.order_by(User.id.desc()).all()
    return render_template("admin/users.html", items=items)


@admin_bp.route("/users/<int:user_id>/toggle-active", methods=["POST"])
@login_required
def toggle_user_active(user_id: int):
    deny = _admin_only()
    if deny:
        return deny

    u = User.query.get_or_404(user_id)
    if u.id == current_user.id:
        flash("Не можеш да деактивираш себе си.")
        return redirect(url_for("admin.users"))

    u.is_active = not bool(u.is_active)
    db.session.commit()

    flash("Обновено.")
    return redirect(url_for("admin.users"))


@admin_bp.route("/services", methods=["GET"])
@login_required
def services():
    deny = _admin_only()
    if deny:
        return deny

    items = Service.query.order_by(Service.id.desc()).all()
    return render_template("admin/services.html", items=items)


@admin_bp.route("/services/<int:service_id>/delete", methods=["POST"])
@login_required
def delete_service(service_id: int):
    deny = _admin_only()
    if deny:
        return deny

    s = Service.query.get_or_404(service_id)
    db.session.delete(s)
    db.session.commit()

    flash("Услугата е изтрита.")
    return redirect(url_for("admin.services"))


@admin_bp.route("/bookings", methods=["GET"])
@login_required
def bookings():
    deny = _admin_only()
    if deny:
        return deny

    items = Booking.query.order_by(Booking.id.desc()).all()
    return render_template("admin/bookings.html", items=items)


@admin_bp.route("/reviews", methods=["GET"])
@login_required
def reviews():
    deny = _admin_only()
    if deny:
        return deny

    items = Review.query.order_by(Review.id.desc()).all()
    return render_template("admin/reviews.html", items=items)


@admin_bp.route("/reviews/<int:review_id>/delete", methods=["POST"])
@login_required
def delete_review(review_id: int):
    deny = _admin_only()
    if deny:
        return deny

    r = Review.query.get_or_404(review_id)
    db.session.delete(r)
    db.session.commit()

    flash("Ревюто е изтрито.")
    return redirect(url_for("admin.reviews"))


@admin_bp.route("/payments", methods=["GET"])
@login_required
def payments():
    deny = _admin_only()
    if deny:
        return deny

    items = Payment.query.order_by(Payment.id.desc()).all()
    return render_template("admin/payments.html", items=items)


@admin_bp.route("/stats", methods=["GET"])
@login_required
def stats():
    deny = _admin_only()
    if deny:
        return deny

    data = {
        "users": User.query.count(),
        "services": Service.query.count(),
        "bookings": Booking.query.count(),
        "reviews": Review.query.count(),
        "payments": Payment.query.count(),
    }
    return render_template("admin/stats.html", data=data)
