from flask import (
    Blueprint,
    redirect,
    render_template,
    render_template_string,
    url_for,
    request,
    flash,
)
from flask_login import current_user, login_required
from werkzeug.security import generate_password_hash
from .models import Ray, User, Like
from . import db


views = Blueprint("views", __name__)


@views.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html", title="Home", user=current_user)


@views.route("/tos")
def tos():
    return render_template("tos.html")


@views.route("/account")
@login_required
def account():
    return render_template(
        "account.html", title=f"{current_user.username}'s Account", user=current_user
    )


@views.route("/profile/<int:id>")
@login_required
def profile(id):
    user = User.query.get(id)
    if not user:
        flash("I'm not sure what you're trying to do. But it doesn't work.")
        return redirect(request.referrer)
    rays = Ray.query.filter_by(user_id=id).all()
    return render_template(
        "profile.html",
        title=f"{current_user.username}'s Profile",
        user=current_user,
        user_profile=user,
        rays=rays,
    )


@views.route("/post-ray", methods=["POST"])
@login_required
def post_ray():
    if request.method == "POST":
        ray = request.form.get("ray")

        if len(ray) < 1:
            flash("Ray is too short!", "danger")
            return redirect(url_for("."))
        else:
            new_ray = Ray(content=ray, user_id=current_user.id)
            db.session.add(new_ray)
            db.session.commit()

            return get_rays()
    return "YAY"


@views.route("/rays")
def get_rays():
    rays = Ray.query.all()
    return render_template("components/ray.html", rays=rays, user=current_user)


@views.route("/delete-ray/<int:id>", methods=["DELETE"])
@login_required
def delRey(id):
    ray = Ray.query.get(id)
    if ray:
        if ray.user_id == current_user.id:
            db.session.delete(ray)
            db.session.commit()
            return get_rays()
        else:
            flash("You are not authorized to delete this note")
            return redirect(url_for("views.index"))
    else:
        flash("I'm not sure what you're trying to do. But it doesn't work.")
        return redirect(url_for("views.index"))


@views.route("/update-info", methods=["POST"])
@login_required
def update_info():
    email = request.form.get("email")
    username = request.form.get("username")
    pronouns = request.form.get("pronouns")
    bio = request.form.get("bio")

    if not email or not username:
        flash("Email and username fields cannot be empty", "danger")
        return redirect(url_for("views.account"))

    email_taken = User.query.filter_by(email=email).first()
    username_taken = User.query.filter_by(username=username).first()
    if email_taken and email != current_user.email:
        flash("That email is already in use", "danger")
        return redirect(url_for("views.account"))
    elif username_taken and username != current_user.username:
        flash("That username is already in use", "danger")
        return redirect(url_for("views.account"))
    else:
        current_user.username = username
        current_user.email = email
        current_user.pronouns = pronouns
        current_user.bio = bio.strip()
        db.session.commit()

    flash("Updated information successfully", "success")
    return redirect(url_for("views.account"))


@views.route("/update-pass", methods=["POST"])
@login_required
def update_pass():
    pass1 = request.form.get("password1")
    pass2 = request.form.get("password2")

    if pass1 != pass2:
        flash("Passwords must match", "danger")
        return redirect(url_for("views.account"))
    elif len(pass1) < 8:
        flash("Password must be 8 characters", "danger")
        return redirect(url_for("views.account"))
    else:
        current_user.password = generate_password_hash(pass1, method="scrypt")
        db.session.commit()
        print(current_user.password == generate_password_hash(pass1))
        flash("Password updated successfully", "success")
        return redirect(url_for("views.account"))


@views.route("/like/<int:rayId>", methods=["POST"])
@login_required
def like(rayId):
    ray = Ray.query.get(rayId)
    like_ = Like.query.filter_by(user_id=current_user.id, ray_id=ray.id).first()
    if not ray:
        flash("I'm not sure what you're trying to do. But it doesn't work.")
        return redirect(url_for("views.index"))
    elif like_:
        db.session.delete(like_)
        db.session.commit()
    else:
        like = Like(user_id=current_user.id, ray_id=ray.id)
        db.session.add(like)
        db.session.commit()

    return render_template_string(
        """{% if user.id in ray.likes|map(attribute="user_id")|list %}
        <button hx-post="{{ url_for('views.like', rayId=ray.id) }}" hx-swap="outerHTML"
            class="btn text-success d-flex align-items-center"><span
                style="font-size: 20px;">{{ray.likes|length}}</span>&nbsp;<span class="material-icons">
                favorite
            </span></button>
        {% else %}
        <button hx-post="{{ url_for('views.like', rayId=ray.id) }}" hx-swap="outerHTML"
            class="btn text-success d-flex align-items-center"><span
                style="font-size: 20px;">{{ray.likes|length}}</span>&nbsp;<span class="material-icons">
                favorite_outline
            </span></button>
        {% endif %}""",
        ray=ray,
        user=current_user,
    )


@views.route("/admin")
def admin():
    if not current_user.is_admin:
        flash("That isn't allowed", "danger")
        return redirect(request.referrer)
    users = User.query.all()
    rays = Ray.query.all()
    return render_template(
        "admin.html", users=users, rays=rays, title="Admin", user=current_user
    )


@views.route("/login")
def login():
    return redirect(url_for("auth.login"))


@views.route("/logout")
def logout():
    return redirect(url_for("auth.logout"))


@views.route("/signup")
def signup():
    return redirect(url_for("auth.signup"))
