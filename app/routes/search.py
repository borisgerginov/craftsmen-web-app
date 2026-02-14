from flask import Blueprint, render_template, request
from app.models.service import Service
from app.models.service_category import ServiceCategory

search_bp = Blueprint("search", __name__)

@search_bp.route("/search", methods=["GET"])
def search():
    q = (request.args.get("q") or "").strip()
    category_id = (request.args.get("category_id") or "").strip()
    location = (request.args.get("location") or "").strip()

    categories = ServiceCategory.query.order_by(ServiceCategory.name.asc()).all()

    query = Service.query

    if category_id.isdigit():
        query = query.filter(Service.category_id == int(category_id))

    if q:
        like = f"%{q}%"
        query = query.filter(Service.title.ilike(like) | Service.description.ilike(like))

    if location:
        query = query.filter(Service.location.ilike(f"%{location}%"))

    results = query.order_by(Service.id.desc()).all()

    return render_template(
        "search/results.html",
        categories=categories,
        results=results,
        q=q,
        category_id=category_id,
        location=location
    )
