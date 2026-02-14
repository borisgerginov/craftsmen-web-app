from flask import Flask
from flask_login import LoginManager
from app.db import db

login_manager = LoginManager()
login_manager.login_view = "main.home"

def seed_categories():
    from app.models.service_category import ServiceCategory

    defaults = [
        "Електротехник",
        "Водопроводчик",
        "Бояджия",
        "Плочкаджия",
        "Гипсокартон",
        "Мебелист",
        "Климатици",
        "Коли"
    ]

    for name in defaults:
        exists = ServiceCategory.query.filter_by(name=name).first()
        if not exists:
            db.session.add(ServiceCategory(name=name))

    db.session.commit()

def create_app(test_config):
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "my-secret"

    import os

    if test_config:
        app.config.update(test_config)
    else:
        db_path = os.path.join(app.instance_path, "app.db")
        os.makedirs(app.instance_path, exist_ok=True)

        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_path
        print("DB FILE ABS =", db_path)


    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login" #zashto?

    from app.models.user import User
    from app.models.profile import Profile
    from app.models.provider_profile import ProviderProfile
    from app.models.service_category import ServiceCategory
    from app.models.service import Service
    from app.models.booking import Booking
    from app.models.review import Review
    from app.models.payment import Payment
    from app.models.favourite import Favourite

    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.profile import profile_bp
    from app.routes.provider import provider_bp
    from app.routes.admin import admin_bp
    from app.routes.provider_service import provider_service_bp
    from app.routes.search import search_bp
    from app.routes.booking import bookings_bp
    from app.routes.provider_booking import provider_bookings_bp
    from app.routes.reviews import reviews_bp
    from app.routes.public import public_bp
    from app.routes.payments import payments_bp
    from app.routes.notifications import notifications_bp
    from app.routes.favourites import favourites_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(provider_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(provider_service_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(provider_bookings_bp)
    app.register_blueprint(reviews_bp)
    app.register_blueprint(public_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(favourites_bp)

    @login_manager.user_loader
    def load_user(user_id: str):
        return User.query.get(int(user_id))

    with app.app_context():
        db.create_all()
        seed_categories()


    return app