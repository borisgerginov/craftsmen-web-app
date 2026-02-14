from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.db import db
from app.models.user import User
from app.models.profile import Profile
from sqlalchemy.exc import IntegrityError


auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Email and password are required.")
            return redirect(url_for("auth.register"))
        
        if User.query.filter_by(email=email).first():
            flash("This email is already registered.")
            return redirect(url_for("auth.register"))
        
        user = User(email=email, role="customer")
        user.set_password(password)

        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            print("INTEGRITY ERROR:", e)
            print("ORIG:", getattr(e, "orig", None))
            flash("IntegrityError: провери терминала (ORIG).")
            return redirect(url_for("auth.register"))

        prof = Profile(user_id=user.id)
        db.session.add(prof)
        db.session.commit

        flash("The registration is successful. Log into your account.")
        return redirect(url_for("auth.login"))
    
    return render_template("auth/register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()
        print("FOUND USER:", bool(user))
        if user:
            print("HASH LEN IN DB:", len(user.password_hash))
        if not user or not user.check_password(password):
            flash("Invalid email or password.")
            return redirect(url_for("auth.login"))
        
        login_user(user)
        return redirect(url_for("main.home"))
    
    return render_template("auth/login.html")

@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("Log out from account.")
    return redirect(url_for("main.home"))