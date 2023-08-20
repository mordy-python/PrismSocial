from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Ray(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    likes = db.Column(db.Integer, default=0)
    content = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User", back_populates="rays")
    likes = db.relationship("Like", backref="ray")


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    is_admin = db.Column(db.Boolean, default=False)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(300))
    username = db.Column(db.String(150))
    avatar = db.Column(db.String(150), nullable=False)
    pronouns = db.Column(db.String(150), default="")
    rays = db.relationship("Ray", back_populates="user")
    likes = db.relationship("Like", backref="user")
    bio = db.Column(db.String(1000))


class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    ray_id = db.Column(db.Integer, db.ForeignKey("ray.id"))
