from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from pathlib import Path
from flask_login import LoginManager
from flask_migrate import Migrate
from pathlib import Path
import os
from dotenv import load_dotenv


base_dir = Path(__file__).parent.resolve()

load_dotenv(base_dir.parent.resolve() / ".env")

db = SQLAlchemy()
DB_NAME = "database.sqlite"


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///" + str(
        base_dir / "db" / DB_NAME
    )
    db.init_app(app)
    migrate = Migrate(app, db)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/auth")

    from .models import User, Ray

    create_db(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_db(app: Flask):
    if not (Path("prism") / DB_NAME).exists():
        with app.app_context():
            db.create_all()
        print("Created database")
