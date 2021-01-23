import os
from flask import Flask, request, abort, jsonify, render_template, abort
from flask.globals import session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import datetime

from models import setup_db, Date, Tenor, Currency, Curve, Spread
from markit import get_markit_yiled


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    cors = CORS(app)

    @app.route('/currencies')
    def get_currencies():
        selection = Currency.query.all()

        if len(selection) == 0:
            abort(404)

        currencies = {currency.id: currency.ccy for currency in selection}

        return jsonify({
            'success': True,
            'status_code': 200,
            'currencies': currencies,
        })
    return app


app = create_app()

'''
Function to populate Tenor table, to be use only for newly created db. 
'''


def commit_tenors():
    tenors = ['1M', '2M', '3M', '6M', '1Y', '2Y', '3Y', '4Y', '5Y',
              '6Y', '7Y', '8Y', '9Y', '10Y', '12Y', '15Y', '20Y', '25Y', '30Y']
    for tenor in tenors:
        Tenor(tenor).insert()


'''
Function to populate Currency table with main currencies, to be use only for newly created db. 
'''


def commit_ccy():
    ccys = ['USD', 'EUR', 'GBP', 'CHF']
    for ccy in ccys:
        Currency(ccy).insert()


def commit_curve(yyyymmdd, CCY):
    ccy = Currency.query.filter_by(ccy=CCY).one_or_none()
    if ccy is None:
        ccy = Currency(CCY)
        ccy.insert()

    date_datetime = datetime.date(
        int(yyyymmdd[:4]), int(yyyymmdd[4:6]), int(yyyymmdd[6:8]))
    date = Date.query.filter_by(date=date_datetime).one_or_none()
    if date is None:
        date = Date(date_datetime)
        date.insert()

    _, yield_dict = get_markit_yiled(yyyymmdd, CCY)
    curve = Curve(date.id, ccy.id)
    curve.insert()

    tenors = Tenor.query.all()
    for tenor in tenors:
        Spread(tenor.id, curve.id, yield_dict[tenor.tenor]).insert()
