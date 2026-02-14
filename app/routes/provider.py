from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.db import db
from app.models.provider_profile import ProviderProfile

provider_bp = Blueprint("provider", __name__)

@provider_bp.route("/provider/apply", methods=["GET", "POST"])
@login_required
def apply():
    existing = ProviderProfile.query.filter_by(provider_id=current_user.id).first()

    if request.method == "POST":
        if existing is not None:
            flash("Вече имаш профил на майстор.")
            return redirect(url_for("provider.status"))
        
        bio = (request.form.get("bio") or "").strip()
        gallery_links = (request.form.get("gallery_links") or "").strip()
        certificates = (request.form.get("certificates") or "").strip()

        pp = ProviderProfile(
            provider_id = current_user.id,
            is_verified = False,
            bio = bio if bio else None,
            gallery_links = gallery_links if gallery_links else None,
            certificates = certificates if certificates else None
        )

        db.session.add(pp)
        db.session.commit()

        flash("Кандидатурата е изпратена ✅ Очаква одобрение от администратор.")
        return redirect(url_for("provider.status"))
    
    return render_template("provider/apply.html", pp=existing)
    

@provider_bp.route("/provider/status", methods = ["GET"])
@login_required
def status():
    pp = ProviderProfile.query.filter_by(provider_id=current_user.id).first()
    return render_template("provider/status.html", pp=pp)