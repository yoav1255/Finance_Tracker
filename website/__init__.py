
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
import requests_cache



db = SQLAlchemy()
DB_NAME = "database.db"


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'sec_key key'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    app.jinja_env.filters['format_number'] = format_number

    return app

def create_database(app):
    with app.app_context():
        if not path.exists('website/' + DB_NAME):
            # db.drop_all()
            db.create_all()
            requests_cache.install_cache('stock_cache', backend='sqlite', expire_after=300)  # 5 minutes expiration
            print("Database Created!")


def format_number(value):
    try:
        value = float(value)
        if value>1_000_000_000_000 or value<-1_000_000_000_000:
            return f'{value/1_000_000_000_000:.2f} T'
        elif value>1_000_000_000 or value<1_000_000_000:
            return f'{value/1_000_000_000:.2f} B'
        elif value>1_000_000 or value<1_000_000:
            return f'{value/1_000_000:.2f} M'
        elif value>1_000 or value<1_000:
            return f'{value/1_000:.2f} K'
        else:
            return value
    except (ValueError, TypeError):
        return value
