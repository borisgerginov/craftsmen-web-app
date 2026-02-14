from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.db import db
from app.models.profile import Profile

profile_bp = Blueprint("profile", __name__)

@profile_bp.route("/profile", methods=["GET", "POST"])
@login_required
def my_profile():
    prof = Profile.query.get(current_user.id)
    if prof is None:
        prof = Profile(user_id=current_user.id)
        db.session.add(prof)
        db.session.commit()

    if request.method == "POST":
        prof.first_name = (request.form.get("first_name") or "").strip()
        prof.last_name = (request.form.get("last_name") or "").strip()
        prof.address = (request.form.get("address") or "").strip()
        prof.preferences = (request.form.get("preferences") or "").strip()

        db.session.commit()
        flash("Профилът бе обновен успешно ✅")
        return redirect(url_for("profile.my_profile"))
    
    return render_template("profile/my_profile.html", prof=prof)
    

