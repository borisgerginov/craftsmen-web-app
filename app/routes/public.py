from flask import Blueprint, render_template
from app.models.user import User
from app.models.profile import Profile
from app.models.provider_profile import ProviderProfile
from app.models.service import Service
from app.models.review import Review
from app.models.booking import Booking

public_bp = Blueprint("public", __name__)

@public_bp.route("/providers/<int:provider_id>", methods=["GET"])
def provider_profile(provider_id: int):
    provider = User.query.get_or_404(provider_id)

    prof = Profile.query.filter_by(user_id=provider.id).first()
    pp = ProviderProfile.query.filter_by(provider_id=provider.id).first()

    services = (Service.query.filter_by(provider_id=provider.id).order_by(Service.id.desc()).all())
    reviews = (Review.query.join(Booking, Review.booking_id == Booking.id).filter(Booking.provider_id == provider.id).order_by(Review.id.desc()).all())

    return render_template(
        "public/provider_profile.html",
        provider=provider,
        prof=prof,
        pp=pp,
        services=services,
        reviews=reviews
    )