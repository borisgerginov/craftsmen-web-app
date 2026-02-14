from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app.db import db
from app.models.booking import Booking
from app.models.review import Review
from app.notifications.notify import notify

reviews_bp = Blueprint("reviews", __name__)

@reviews_bp.route("/bookings/<int:booking_id>/review", methods=["GET", "POST"])
@login_required
def add_review(booking_id: int):
    if current_user.role != "customer":
        flash("Само клиенти могат да оставят ревю.")
        return redirect(url_for("main.home"))
    
    b = Booking.query.get_or_404(booking_id)

    if b.status != "completed":
        flash("Можеш да оставиш ревю само след като услугата е завършена.")
        return redirect(url_for("bookings.my_bookings"))
    
    existing = Review.query.filter_by(booking_id=b.id).first()
    if existing:
        flash("Вече си оставил ревю за тази услуга.")
        return redirect(url_for("reviews.view_review", review_id=existing.id))
    
    if request.method == "POST":
        rating_raw = (request.form.get("rating") or "").strip()
        comment = (request.form.get("comment") or "").strip()

        if not rating_raw.isdigit():
            flash("Избери рейтинг 1-5.")
            return redirect(url_for("reviews.add_review", booking_id=b.id))
        
        rating = int(rating_raw)
        if rating < 1 or rating > 5:
            flash("Рейтингът трябва да е между 1 и 5.")
            return redirect(url_for("reviews.add_review", booking_id=b.id))
        
        r = Review(booking_id=b.id, rating=rating, comment=comment if comment else None)
        db.session.add(r)
        db.session.commit()

        flash("Ревюто е добавено ✅")
        notify(b.provider_id, f"Клиентът остави ревю за booking #{b.id}")
        return redirect(url_for("bookings.my_bookings"))
    
    return render_template("reviews/add.html", b=b)

@reviews_bp.route("/reviews/<int:review_id>", methods=["GET"])
def view_review(review_id: int):
    r = Review.query.get_or_404(review_id)

    return render_template("reviews/view.html", r=r)
