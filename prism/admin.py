from flask import Blueprint, render_template, flash, redirect, url_for
from .models import User, Ray
from flask_login import current_user

admin = Blueprint("admin", __name__)


@admin.route("/")
def home():
    if not current_user.is_admin:
        flash("That isn't allowed", "danger")
        return redirect(url_for("views.index"))
    users = User.query.all()
    rays = Ray.query.all()
    return render_template(
        "admin.html", users=users, rays=rays, title="Admin", user=current_user
    )
