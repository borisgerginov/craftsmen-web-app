from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.db import db
from app.models.service import Service
from app.models.service_category import ServiceCategory
from app.models.provider_profile import ProviderProfile

provider_service_bp = Blueprint("provider_service", __name__)

def deny_if_not_verified_provider():
    if current_user.role != "provider":
        flash("Само одобрени майстори имат достъп до тази страница.")
        return redirect(url_for("main.home"))
    
    pp = ProviderProfile.query.filter_by(provider_id=current_user.id).first()
    if not pp:
        flash("Нямаш профил на майстор. Кандидатствай първо.")
        return redirect(url_for("provider.apply"))
    
    if not pp.is_verified:
        flash("Профилът ти все още не е одобрен.")
        return redirect(url_for("provider.status"))
    
    return None

@provider_service_bp.route("/provider/services", methods=["GET"])
@login_required
def list_services():
    deny = deny_if_not_verified_provider()
    if deny:
        return deny
    
    services = (Service.query.filter_by(provider_id=current_user.id).order_by(Service.id.desc()).all())

    return render_template("provider/services_list.html", services=services)

@provider_service_bp.route("/provider/services/new", methods=["GET", "POST"])
@login_required
def new_service():
    deny = deny_if_not_verified_provider()
    if deny:
        return deny
    
    categories = ServiceCategory.query.order_by(ServiceCategory.name.asc()).all()

    if request.method == "POST":
        category_id = (request.form.get("category_id") or "").strip()
        title = (request.form.get("title") or "").strip()
        description = (request.form.get("description") or "").strip()
        location = (request.form.get("location") or "").strip()
        price_raw = (request.form.get("price") or "").strip()

        if not category_id.isdigit() or not title:
            flash("Категория и заглавие са задължителни.")
            return redirect(url_for("provider_service.new_service"))
        
        price = int(price_raw) if price_raw.isdigit() else None

        s = Service(
            provider_id = current_user.id,
            category_id = int(category_id),
            title = title,
            description = description if description else None,
            location = location if location else None,
            price = price
        )

        db.session.add(s)
        db.session.commit()

        flash("Услугата е създадена ✅")
        return redirect(url_for("provider_service.list_services"))
    
    return render_template("provider/services_new.html", categories=categories)


@provider_service_bp.route("/provider/services/<int:service_id>/edit", methods=["GET", "POST"])
@login_required
def edit_service(service_id: int):
    deny = deny_if_not_verified_provider()
    if deny:
        return deny
    
    s = Service.query.get_or_404(service_id)

    if s.provider_id != current_user.id:
        flash("Нямаш права да редактираш тази услуга.")
        return redirect(url_for("provider_service.list_services"))
    
    categories = ServiceCategory.query.order_by(ServiceCategory.name.asc()).all()

    if request.method == "POST":
        category_id = (request.form.get("category_id") or "").strip()
        title = (request.form.get("title") or "").strip()
        description = (request.form.get("description") or "").strip()
        location = (request.form.get("location") or "").strip()
        price_raw = (request.form.get("price") or "").strip()

        if not category_id.isdigit() or not title:
            flash("Категория и заглавие са задължителни.")
            return redirect(url_for("provider_service.edit_service", service_id=service_id))

        s.category_id = int(category_id)
        s.title = title
        s.description = description if description else None
        s.location = location if location else None
        s.price = int(price_raw) if price_raw.isdigit() else None

        db.session.commit()
        flash("Запазено ✅")
        return redirect(url_for("provider_service.list_services"))

    return render_template("provider/services_edit.html", s=s, categories=categories)

@provider_service_bp.route("/provider/services/<int:service_id>/delete", methods=["POST"])
@login_required
def delete_service(service_id: int):
    deny = deny_if_not_verified_provider()
    if deny:
        return deny
    
    s = Service.query.get_or_404(service_id)

    if s.provider_id != current_user.id:
        flash("Нямаш права да изтриеш тази услуга.")
        return redirect(url_for("provider_service.list_services"))
    
    db.session.delete(s)
    db.session.commit()
    flash("Изтрито.")
    return redirect(url_for("provider_service.list_services"))