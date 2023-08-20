from flask import Blueprint, flash, render_template, request, redirect, url_for
from .models import User
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user, login_user, logout_user, login_required
import random


auth = Blueprint("auth", __name__)


def gen_avatar(username):
    styles = [
        "Backpack",
        "Browser",
        "Cat",
        "CreditCard",
        "File",
        "Ghost",
        "IceCream",
        "Mug",
        "Planet",
        "SpeechBubble",
    ]
    url = f"https://kawaii-avatar.now.sh/api/avatar?username={username}&type={random.choice(styles)}&background=%23766dd2"
    return url


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.form
        username = data.get("username")
        password = data.get("password")

        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                flash("Successfully logged in!", "success")
                return redirect(url_for("views.index"))
            else:
                flash("Incorrect username or password", "danger")
        else:
            flash("Incorrect username or password", "danger")
    return render_template("login.html", title="Login", user=current_user)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@auth.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        data = request.form
        email = data.get("email")
        username = data.get("username")
        pass1 = data.get("password1")
        pass2 = data.get("password2")

        user = User.query.filter_by(email=email).first()
        if user:
            flash(
                "An account with that email already exists. Try <a href='/auth/login'>logging in</a>."
            )
        elif len(username) < 3:
            flash("Username must be longer than 3 characters", "danger")
        elif pass1 != pass2:
            flash("Passwords must match", "danger")
        elif len(pass1) < 8:
            flash(
                "Your password is too short. It must be at least 8 characters", "danger"
            )
        else:
            new_user = User(
                email=email,
                username=username,
                password=generate_password_hash(pass1, method="scrypt"),
                avatar=gen_avatar(username),
            )
            db.session.add(new_user)
            db.session.commit()

            login_user(new_user, remember=True)
            flash("Account created", "success")
            return redirect(url_for("views.index"))

    return render_template("signup.html", title="Sign Up", user=current_user)
