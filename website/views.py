from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user

from dotenv import load_dotenv
import os
import requests
from . import db
import yfinance as yf
from .models import Watchlist, Portfolio, Holding
import pandas as pd
import matplotlib.pyplot as plt
import requests
from .helpers import determine_style, calculate_future_value, calculate_intrinsic_value, calculate_annual_growth_rate, \
    get_random_color
import numpy as np

load_dotenv()
FMP_API_KEY = os.getenv('FMP_API_KEY')

#TODO enable smart search
plt.style.use("ggplot")

views = Blueprint('views', __name__)


def update_portfolio_stock(stock):
    stock.average_price = 0
    stock.amount_stocks = 0
    for holding in stock.holdings:
        print(holding)
        stock.average_price += holding.purchased_price * holding.amount_stocks
        stock.amount_stocks += holding.amount_stocks
    if len(stock.holdings) == 0:
        stock.average_price = 0
        stock.amount_stocks = 0
    else:
        stock.average_price /= stock.amount_stocks
        stock.average_price = round(stock.average_price, 2)
    db.session.commit()


def fetch_stock_info(symbol):
    stock_info = None
    error = False
    try:
        url = f'https://financialmodelingprep.com/api/v3/profile/{symbol}?apikey={FMP_API_KEY}'
        response = requests.get(url)
        stock_info = response.json()[0]
    except Exception as e:
        error = True

    return stock_info, error


def is_stock_in_watchlist(symbol, user, error):
    for stock in user.stocks_watchlist:
        if stock.symbol == symbol:
            flash(f' {symbol} already exists ', category="error")
            error = True
    return error


def add_stock_to_watchlist(symbol, current_price, price_target=0):
    stock = Watchlist(symbol=symbol, price=current_price, user_id=current_user.id, price_target=price_target)
    db.session.add(stock)
    db.session.commit()
    flash("Stock added successfully to your watchlist", category="success")


#TODO add diffrent from value
#TODO add email notification when target price hit
@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    stock_info = None
    if request.method == 'POST':
        symbol = request.form.get('symbol').upper()
        stock_info, error = fetch_stock_info(symbol)
        error = is_stock_in_watchlist(symbol, current_user, error)

        if not error:
            add_stock_to_watchlist(symbol, stock_info['price'])

    return render_template("home.html", user=current_user, stock_info=stock_info)


@views.route('/portfolio', methods=['GET', 'POST'])
@login_required
def show_portfolio():
    total_value = 0
    initial_value = 0
    stock_names = []
    stock_info = None
    stock_allocations = []
    colors = []
    i = 0

    for stock in current_user.stocks_portfolio:
        if stock.amount_stocks > 0:
            print(stock.amount_stocks)
            total_value += stock.current_price * stock.amount_stocks
            initial_value += stock.average_price * stock.amount_stocks

    initial_value = round(initial_value, 2)
    total_value = round(total_value, 2)

    for stock in current_user.stocks_portfolio:
        if stock.amount_stocks > 0:
            stock_names.append(stock.symbol)
            alloc = round(((stock.amount_stocks * stock.current_price) / total_value) * 100, 2)
            stock_allocations.append(alloc)
            colors.append(get_random_color())

    if request.method == 'POST':
        if 'add_to_portfolio_button' in request.form:
            symbol = request.form.get('symbol').upper()
            stock_info, error = fetch_stock_info(symbol)

            if symbol in stock_names:
                error = True
                flash(f"Stock {symbol} already exists", category="error")
            if not error:
                stock = Portfolio(symbol=symbol, current_price=stock_info['price'], amount_stocks=0,
                                  user_id=current_user.id)
                db.session.add(stock)
                db.session.commit()
                flash("Stock added successfully to your portfolio", category="success")

        elif 'add_holding_button' in request.form:
            purchased_price = (request.form.get('price_purchased'))
            amount_stocks = (request.form.get('amount_purchased'))
            stock_id = (request.form.get('stock_id'))
            if not purchased_price or not amount_stocks:
                flash("ERROR", category="error")
            else:
                holding = Holding(amount_stocks=amount_stocks, purchased_price=purchased_price, stock_id=stock_id)
                db.session.add(holding)
                db.session.commit()
                stock = Portfolio.query.get(stock_id)
                update_portfolio_stock(stock)
                flash("Holding added successfully", category="success")

    return render_template("portfolio.html", user=current_user, stock_info=stock_info,
                           total_value=total_value, initial_value=initial_value,
                           determine_style=determine_style,
                           stock_names=stock_names, stock_allocations=stock_allocations, colors=colors)


@views.route('/delete-watchlist', methods=['POST'])
def delete_watchlist():
    symbol_id = request.json.get('symbol_id')
    symbol = Watchlist.query.get(symbol_id)
    if symbol and symbol.user_id == current_user.id:
        db.session.delete(symbol)
        db.session.commit()

    return jsonify({})


@views.route('/delete-portfolio', methods=['POST'])
def delete_portfolio():
    symbol_id = request.json.get('symbol_id')
    symbol = Portfolio.query.get(symbol_id)
    if symbol and symbol.user_id == current_user.id:
        db.session.delete(symbol)
        db.session.commit()

    return jsonify({})


@views.route('/delete-holding', methods=['POST'])
def delete_holding():
    holding_id = request.json.get('holding_id')
    holding = Holding.query.get(holding_id)
    print(holding)
    if holding:
        db.session.delete(holding)
        db.session.commit()
        stock = Portfolio.query.get(holding.stock_id)
        update_portfolio_stock(stock)
    return jsonify({})


#todo handle stats, we need to url to fetch the data from
#todo quarterly statements only for subscription
#todo balance sheet and cash flow statements doesnt work
@views.route('/stock/<symbol>', methods=['GET', 'POST'])
@login_required
def show_stock(symbol):
    selected_statement = request.args.get('selected_statement', default='income-statement')
    selected_period = request.args.get('selected_period', default='annual')
    print(f'selected_statement: {selected_statement}')

    stats = False
    stock_info = []
    profile = []
    key_metrics = []
    ratios = []

    if selected_statement == 'stats':
        stats = True
    try:
        if not stats:
            url = f'https://financialmodelingprep.com/api/v3/{selected_statement}/{symbol}?period={selected_period}&apikey={FMP_API_KEY}'
            stock_info = requests.get(url).json()

        else:
            url = f'https://financialmodelingprep.com/api/v3/income-statement/{symbol}/period=annual?apikey={FMP_API_KEY}'
            url_profile = f'https://financialmodelingprep.com/api/v3/profile/{symbol}?apikey={FMP_API_KEY}'
            url_key_metrics = f'https://financialmodelingprep.com/api/v3/key-metrics-ttm/{symbol}?apikey={FMP_API_KEY}'
            url_ratios = f'https://financialmodelingprep.com/api/v3/ratios-ttm/{symbol}?apikey={FMP_API_KEY}'
            stock_info=requests.get(url).json()
            profile = requests.get(url_profile).json()
            key_metrics = requests.get(url_key_metrics).json()
            ratios = requests.get(url_ratios).json()


    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
    except requests.RequestException as e:
        # Handle request-related exceptions (e.g., ConnectionError, Timeout, etc.)
        print(f"An error occurred: {e}")

    return render_template("stock-overview.html", user=current_user, symbol=symbol,
                           selected_statement=selected_statement, selected_period=selected_period,
                           stock_info=stock_info, stats=stats, num_periods=len(stock_info),ratios=ratios,profile=profile,key_metrics=key_metrics)


@views.route('/stock/<symbol>/calculations', methods=['GET', 'POST'])
@login_required
def show_calculations(symbol):
    stock = yf.Ticker(symbol)
    statement = stock.get_income_stmt()
    current_price = 0
    incomes = []
    periods = []
    per = statement.columns[len(statement.columns) - 1]
    statement.columns = pd.to_datetime(statement.columns)
    for period in statement.columns:
        periods.append(period)
        incomes.append(statement[period]['TotalRevenue'])
    revenue_growth_rate_percentage = calculate_annual_growth_rate(incomes[len(incomes) - 1], incomes[0], len(incomes))

    #TODO fix issues with missing data
    try:
        stock_info = stock.info
        #financials
        print(stock_info)
        current_price = stock_info['currentPrice']
        fcf = stock_info.get('freeCashflow', 1)
        ebitda = stock_info['ebitda']
        eps = stock_info['trailingEps']
        market_cap = stock_info["marketCap"]

        shares_outstanding = stock_info['sharesOutstanding']
        current_pe = stock_info["trailingPE"]
        current_ev_to_ebitda = stock_info["enterpriseToEbitda"]
        current_pfcf = market_cap / fcf
        current_net_margin = stock_info["profitMargins"]
        current_ebitda_margin = stock_info["ebitdaMargins"]
        current_revenue = stock_info["totalRevenue"]
        current_fcf_margin = float(fcf / current_revenue)
        enterprise_value = stock_info["enterpriseValue"]

    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
    except requests.RequestException as e:
        # Handle request-related exceptions (e.g., ConnectionError, Timeout, etc.)
        print(f"An error occurred: {e}")

    if request.method == 'POST':
        if 'calculate' in request.form:
            #inputs:
            revenue_growth_rate = float(request.form.get('revenueGrowthRate')) / 100

            ebitda_margin = float(request.form.get("ebitdaMargin")) / 100
            net_margin = float(request.form.get("netMargin")) / 100
            fcf_margin = float(request.form.get("fcfMargin")) / 100

            future_pe = int(request.form.get('futurePE'))
            future_ev_ebitda = int(request.form.get('futureEVEBITDA'))
            future_pfcf = int(request.form.get('futurePFCF'))
            shares_growth = float(request.form.get('sharesGrowth')) / 100

            ror = float(request.form.get('returnRate')) / 100
            num_of_years = int(request.form.get('numOfYears'))

            dcf_value = calculate_intrinsic_value(market_cap, current_revenue, revenue_growth_rate, fcf, fcf_margin,
                                                  future_pfcf, ror, num_of_years, shares_outstanding,
                                                  shares_growth).__round__(2)
            eps_value = calculate_intrinsic_value(market_cap, current_revenue, revenue_growth_rate, eps, net_margin,
                                                  future_pe, ror, num_of_years, shares_outstanding,
                                                  shares_growth).__round__(2)
            ebitda_value = calculate_intrinsic_value(enterprise_value, current_revenue, revenue_growth_rate, ebitda,
                                                     ebitda_margin, future_ev_ebitda, ror, num_of_years,
                                                     shares_outstanding, shares_growth).__round__(2)

            return render_template("calculations.html", user=current_user, symbol=symbol, dcf_value=dcf_value,
                                   eps_value=eps_value, ebitda_value=ebitda_value, current_price=current_price,
                                   ebitda_margin=round(ebitda_margin * 100, 2),
                                   revenue_growth_rate=round(revenue_growth_rate * 100, 2),
                                   net_margin=round(net_margin * 100, 2), fcf_margin=round(fcf_margin * 100, 2),
                                   future_pe=future_pe, future_ev_ebitda=future_ev_ebitda,
                                   future_pfcf=future_pfcf, shares_growth=round(shares_growth * 100, 2),
                                   ror=round(ror * 100, 2), num_of_years=num_of_years,
                                   current_pe=round(current_pe, 2), current_ev_to_ebitda=round(current_ev_to_ebitda, 2),
                                   current_pfcf=round(current_pfcf, 2),
                                   current_net_margin=round(current_net_margin * 100, 2),
                                   current_ebitda_margin=round(current_ebitda_margin * 100, 2),
                                   current_fcf_margin=round(current_fcf_margin * 100, 2),
                                   revenue_growth_rate_percentage=revenue_growth_rate_percentage)
        elif 'add_price' in request.form:
            exists = False
            buy_price = int(request.form.get('buyPrice'))
            for stock in current_user.stocks_watchlist:
                if stock.symbol == symbol:
                    exists = True
                    stock.price_target = buy_price
            if exists == False:
                add_stock_to_watchlist(symbol, current_user, current_price, buy_price)
            flash(f'Target price added successfully!', 'success')
        db.session.commit()

    return render_template("calculations.html", user=current_user, symbol=symbol, current_price=current_price,
                           current_pe=round(current_pe, 2), current_ev_to_ebitda=round(current_ev_to_ebitda, 2),
                           current_pfcf=round(current_pfcf, 2),
                           current_net_margin=round(current_net_margin * 100, 2),
                           current_ebitda_margin=round(current_ebitda_margin * 100, 2),
                           current_fcf_margin=round(current_fcf_margin * 100, 2),
                           revenue_growth_rate_percentage=revenue_growth_rate_percentage)
