from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.schedulers import SchedulerAlreadyRunningError
import time
from website.models import Watchlist, Portfolio, Holding,User
from flask import Flask
from main import app
from website import db
from sqlalchemy.orm import aliased
from flask_login import login_required,current_user
import yfinance as yf


def update_stocks():
    symbols_portfolio = get_distinct_symbols_Portfolio()
    symbols_watchlist = get_distinct_symbols_Watchlist()

    data_portfolio = yf.download(symbols_portfolio, period="1d")
    data_watchlist = yf.download(symbols_watchlist, period="1d")

    for symbol in symbols_portfolio:
        try:
            # Get the latest price for the symbol
            latest_price = data_portfolio['Close'][symbol].iloc[0]

            # Update the current_price for all portfolios with this symbol
            stocks = Portfolio.query.filter_by(symbol=symbol).all()
            for stock in stocks:
                stock.current_price = latest_price

            # Commit the changes to the database
            db.session.commit()
        except Exception as e:
            print(f"Error updating {symbol}: {e}")

    for symbol in symbols_watchlist:
        try:
            # Get the latest price for the symbol
            latest_price = data_watchlist['Close'][symbol].iloc[0]

            # Update the current_price for all portfolios with this symbol
            stocks = Watchlist.query.filter_by(symbol=symbol).all()
            for stock in stocks:
                stock.price = latest_price

            # Commit the changes to the database
            db.session.commit()
        except Exception as e:
            print(f"Error updating {symbol}: {e}")

def get_distinct_symbols_Portfolio():
    # Use a subquery to get distinct symbols from the portfolios
    subquery = db.session.query(Portfolio.symbol).distinct().subquery()

    # Use the subquery to fetch distinct symbols
    distinct_symbols = db.session.query(subquery.c.symbol).all()

    # Extract symbols from the result and return as a list
    symbols_list = [row[0] for row in distinct_symbols]

    return symbols_list

def get_distinct_symbols_Watchlist():
    # Use a subquery to get distinct symbols from the portfolios
    subquery = db.session.query(Watchlist.symbol).distinct().subquery()

    # Use the subquery to fetch distinct symbols
    distinct_symbols = db.session.query(subquery.c.symbol).all()

    # Extract symbols from the result and return as a list
    symbols_list = [row[0] for row in distinct_symbols]

    return symbols_list

def scheduled_task():
    # Access the database within the scheduler
    with app.app_context():
        update_stocks()

scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_task, 'interval', days=1)

if __name__ == '__main__':
    try:
        scheduled_task()
        scheduler.start()
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("Scheduler shut down successfully!")


