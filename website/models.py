import datetime
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime
from jinja2 import Template

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import aliased


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    stocks_watchlist = db.relationship('Watchlist')
    stocks_portfolio = db.relationship('Portfolio')


class Watchlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(150), unique=True)
    price = db.Column(db.Integer)
    price_target = db.Column(db.Integer, default=0)
    notified = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(150), unique=True)
    current_price = db.Column(db.Integer)
    average_price = db.Column(db.Integer)
    amount_stocks = db.Column(db.Integer)

    holdings = db.relationship('Holding')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Holding(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount_stocks = db.Column(db.Integer)
    purchased_price = db.Column(db.Integer)
    purchased_date = db.Column(db.DateTime(timezone=True), default=datetime.now())
    stock_id = db.Column(db.Integer, db.ForeignKey('portfolio.id'))
