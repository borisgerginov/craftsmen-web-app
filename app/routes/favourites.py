from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app.db import db
from app.models.favourite import Favourite
from app.models.service import Service

favourites_bp = Blueprint("favourites", __name__)


@favourites_bp.route("/favourites", methods=["GET"])
@login_required
def list_favourites():
    if current_user.role != "customer":
        flash("Само клиенти имат любими.")
        return redirect(url_for("main.home"))

    items = (db.session.query(Favourite, Service)
             .join(Service, Favourite.service_id == Service.id)
             .filter(Favourite.customer_id == current_user.id)
             .order_by(Favourite.id.desc())
             .all())

    return render_template("favourites/list.html", items=items)


@favourites_bp.route("/favourites/add/<int:service_id>", methods=["POST"])
@login_required
def add_favourite(service_id: int):
    if current_user.role != "customer":
        flash("Само клиенти могат да добавят любими.")
        return redirect(url_for("main.home"))

    s = Service.query.get_or_404(service_id)

    existing = Favourite.query.filter_by(customer_id=current_user.id, service_id=s.id).first()
    if existing:
        flash("Вече е в любими.")
        return redirect(request.referrer or url_for("favourites.list_favourites"))

    fav = Favourite(customer_id=current_user.id, service_id=s.id)
    db.session.add(fav)
    db.session.commit()

    flash("Добавено в любими ✅")
    return redirect(request.referrer or url_for("favourites.list_favourites"))


@favourites_bp.route("/favourites/remove/<int:service_id>", methods=["POST"])
@login_required
def remove_favourite(service_id: int):
    if current_user.role != "customer":
        flash("Само клиенти могат да махат любими.")
        return redirect(url_for("main.home"))

    fav = Favourite.query.filter_by(customer_id=current_user.id, service_id=service_id).first()
    if not fav:
        flash("Не е в любими.")
        return redirect(request.referrer or url_for("favourites.list_favourites"))

    db.session.delete(fav)
    db.session.commit()

    flash("Премахнато от любими.")
    return redirect(request.referrer or url_for("favourites.list_favourites"))