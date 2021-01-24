import os
from flask import Flask, request, abort, jsonify, render_template, abort
from flask.globals import session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import datetime

from models import setup_db, Date, Tenor, Currency, Curve, Spread
from markit import get_markit_yiled

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

    date_datetime = to_datetime(yyyymmdd)
    date = Date.query.filter_by(date=date_datetime).one_or_none()

    _, yield_dict = get_markit_yiled(yyyymmdd, CCY)

    curve = Curve(date_id=date.id, ccy_id=ccy.id)
    curve.insert()

    tenors = Tenor.query.all()
    for tenor in tenors:
        Spread(tenor.id, curve.id, yield_dict[tenor.tenor]).insert()


# deleteing tenor, ccy and date will clear db by cascade deletation
def delete_data():
    [tenor.delete() for tenor in Tenor.query.all()]
    [ccy.delete() for ccy in Currency.query.all()]
    [date.delete() for date in Date.query.all()]


def to_datetime(yyyymmdd):
    return datetime.date(
        int(yyyymmdd[:4]), int(yyyymmdd[4:6]), int(yyyymmdd[6:8]))


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

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

    @app.route('/dates')
    def get_dates():
        selection = Date.query.all()

        if len(selection) == 0:
            abort(404)

        dates = {date.id: date.date for date in selection}

        return jsonify({
            'success': True,
            'status_code': 200,
            'dates': dates,
        }), 200

    @app.route('/currencies/<int:ccy_id>')
    def get_currency(ccy_id):
        selection = Currency.query.all()

        if len(selection) == 0:
            abort(404)

        currencies = {currency.id: currency.ccy for currency in selection}

        return jsonify({
            'success': True,
            'status_code': 200,
            'currencies': currencies,
        }), 200

    @app.route('/curves', methods=['POST'])
    def post_curve():
        body = request.get_json()
        yyyymmdd = body.get('date')
        currency = body.get('ccy')

        ccy = Currency.query.filter_by(ccy=currency).one_or_none()
        if ccy is None:
            abort(404, f"There is no currency {currency}")

        date_datetime = to_datetime(yyyymmdd)
        date = Date.query.filter_by(date=date_datetime).one_or_none()

        if date is None:
            date = Date(date_datetime)
            date.insert()

        yield_dict = get_markit_yiled(yyyymmdd, currency)[1]
        curve = Curve(date.id, ccy.id)
        try:
            curve.insert()
        except:
            abort(409, "Curve already exist")

        tenors = Tenor.query.all()
        for tenor in tenors:
            Spread(tenor.id, curve.id, yield_dict[tenor.tenor]).insert()

        tenor_5y = Tenor.query.filter_by(tenor='5Y').one()
        try:
            spread = Spread.query.filter_by(
                curve_id=curve.id, tenor_id=tenor_5y.id).one()
        except:
            abort(422, "Unable to query 5y spread for posted curve.")

        return jsonify({
            'success': True,
            'status_code': 200,
            'curve': {'date_id': curve.date_id, 'ccy_id': curve.ccy_id},
            'spread': spread.spread,
        }), 200

    @app.route('/curves', methods=['PATCH'])
    def patch_curve():
        body = request.get_json()
        yyyymmdd = body.get('date')
        currency = body.get('ccy')
        override = body.get('override')

        ccy = Currency.query.filter_by(ccy=currency).one_or_none()
        date = Date.query.filter_by(date=to_datetime(yyyymmdd)).one_or_none()

        try:
            curve = Curve.query.filter_by(date_id=date.id, ccy_id=ccy.id).one()
        except:
            abort(
                404, f"There is no curve with for currency {currency} at date {to_datetime(yyyymmdd)}")
        try:
            for tenor_key in override.keys():
                tenor = Tenor.query.filter_by(tenor=tenor_key).one()
                spread = Spread.query.filter_by(
                    curve_id=curve.id, tenor_id=tenor.id).one()
                spread.spread = override[tenor_key]
                spread.update()
        except:
            abort(422, "Incorrect override")

        return jsonify({
            'success': True,
            'status_code': 200,
            'curve': {'date_id': curve.date_id, 'ccy_id': curve.ccy_id},
            'spread': 0.002020,
        }), 200

    @app.route('/curves', methods=['DELETE'])
    def delete_curve():
        body = request.get_json()
        yyyymmdd = body.get('date')
        currency = body.get('ccy')

        date_datetime = to_datetime(yyyymmdd)
        date = Date.query.filter_by(date=date_datetime).one_or_none()

        ccy = Currency.query.filter_by(ccy=currency).one_or_none()

        try:
            curve = Curve.query.filter_by(date_id=date.id, ccy_id=ccy.id).one()
        except:
            abort(
                404, f"There is no curve with for currency {currency} at date {date_datetime}")
        try:
            curve.delete()
        except:
            abort(422, "Unable to delete!")

        return jsonify({
            'success': True,
            'status_code': 200,
            'curve': {'date_id': date.id, 'ccy_id': ccy.id},
        }), 200

    @app.errorhandler(422)
    def already_exist(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": error.description
        }), 422

    @app.errorhandler(409)
    def already_exist(error):
        return jsonify({
            "success": False,
            "error": 409,
            "message": error.description
        }), 409

    @app.errorhandler(404)
    def already_exist(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": error.description
        }), 404

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
