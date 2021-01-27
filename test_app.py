import unittest
import json
import datetime
from flask_migrate import downgrade, upgrade
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy.sql.expression import false

from app import create_app, commit_ccy, commit_tenors, commit_curve, to_datetime, delete_data
from models import Currency, Date, Tenor, Curve, Spread, setup_db, db_user, db_password, db_host


class MarkitTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "markit_test"
        self.database_path = f'postgresql://{db_user}:{db_password}@{db_host}/{self.database_name}'
        setup_db(self.app, self.database_path)
        # authorization test
        self.test_client = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkpmWGJjTGxrSXRwelhxUTVRc3pBSSJ9.eyJpc3MiOiJodHRwczovL3RvbWFzenRvbWFzei5ldS5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjAwZjE1NmZjZTI1ODkwMDcxOTY5Y2Q1IiwiYXVkIjoibWFya2l0IiwiaWF0IjoxNjExNzc1Mzg3LCJleHAiOjE2MTE4NjE3ODcsImF6cCI6IkJtWHFyTzlpdEdmaEx5YmgzMHNDVUVIWkY5UjNQRm5RIiwic2NvcGUiOiIiLCJwZXJtaXNzaW9ucyI6WyJnZXQ6Y3VycmVuY3kiLCJnZXQ6Y3VydmUiLCJnZXQ6ZGF0ZSJdfQ.ekwDNgULCwwmGrfPTlPzNg8d9gOQ3uO_TqbEYdfogLAwZcNLYayXOPqvXSZYp5omuw81E-Qsfax4vfQZ3tyvouzatsEiBazkyRje4p8hv8TIS0lXSMgHZS9Oa4XMu11jx0EFSokKkXFT_9cNTiYxxUKbejboxRkaloNryOBfa82cLPsTLNkpN9nQAsMd-CLjGLCf4o8a6cZOiyTPq_q6oDQRi8-YFoSwKzH17l86lJ7YhRZ_cAImv3m8Yz9VC3oCjz_HdiKNC3wAqCjbHVE4IsA9oRhPbCwi25OtbdKA6lpxrMC7Q8nBxewcrAkLgcexF67UwKh2YxOxzOkZzaBxUg"
        self.test_quant = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkpmWGJjTGxrSXRwelhxUTVRc3pBSSJ9.eyJpc3MiOiJodHRwczovL3RvbWFzenRvbWFzei5ldS5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjAwZjE1ZTgyMGFhMTcwMDZhYzcxM2EwIiwiYXVkIjoibWFya2l0IiwiaWF0IjoxNjExNzc1MjU2LCJleHAiOjE2MTE4NjE2NTYsImF6cCI6IkJtWHFyTzlpdEdmaEx5YmgzMHNDVUVIWkY5UjNQRm5RIiwic2NvcGUiOiIiLCJwZXJtaXNzaW9ucyI6WyJkZWxldGU6Y3VydmUiLCJnZXQ6Y3VycmVuY3kiLCJnZXQ6Y3VydmUiLCJnZXQ6ZGF0ZSIsInBhdGNoOmN1cnZlIiwicG9zdDpjdXJ2ZSJdfQ.ZqiVrJl4MQ3U5xSfqYJwRCKHdRn_witfamCul5L88PwIt9QANdN9oLqjTm5carc_njzS5Dhop0TjtX7uoZeBHwQ4PuPV-Y1ddpfUwX1OtJMUGAcvPbVkglEnBwlee6dFWieHCUkz1qrW8exaDIguJTADaDGGndddp0eQftqjfyvHBMy2hdSuqVQWbpEV7Dw1PMS6y1_gnXqwqfDrmf4WHpPD20EEVwdmFzFWhWdWWoQMZw389oRjYGJSANmESKQ2Ek0kugz-L6QtFD28HjydG8dLmJ6K6RGdeQ7oOzzYx57y2Q0NYMZHY71KoI02cLRK6CqSQjpSNhzcJQ8gEDbYZA"
        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all table
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    # to create context for tests
    def insert_and_delete(func):
        def wrapper(self):
            commit_tenors()
            commit_ccy()

            currency = 'USD'
            yyyymmdd = '20201231'
            date_datetime = to_datetime(yyyymmdd)
            Date(date_datetime).insert()

            commit_curve(yyyymmdd=yyyymmdd, CCY=currency)
            try:
                func(self)
            except:
                delete_data()
                raise

            delete_data()
        return wrapper

    '''
    Tests for client role access
    '''

    @insert_and_delete
    def test_get_currencies_client(self):
        res = self.client().get('/currencies', headers={'Authorization':
                                                        'Bearer ' + self.test_client})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(type(data['currencies']), dict)

    @insert_and_delete
    def test_get_dates_client(self):
        res = self.client().get('/dates', headers={'Authorization':
                                                   'Bearer ' + self.test_client})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(type(data['dates']), dict)

    @ insert_and_delete
    def test_post_request_curve_id_client(self):
        date_datetime = datetime.date(2020, 12, 31)
        ccy = Currency.query.filter_by(ccy='USD').one_or_none()
        date = Date.query.filter_by(date=date_datetime).one_or_none()

        curve = Curve.query.filter_by(date_id=date.id, ccy_id=ccy.id).one()

        res = self.client().post('/curves/id', json={'ccy': 'USD',
                                                     'date': '20201231'}, headers={'Authorization':
                                                                                   'Bearer ' + self.test_client})

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['curve_id'], curve.id)

    @ insert_and_delete
    def test_get_curve_by_id_client(self):
        date_datetime = datetime.date(2020, 12, 31)
        ccy = Currency.query.filter_by(ccy='USD').one_or_none()
        date = Date.query.filter_by(date=date_datetime).one_or_none()

        curve = Curve.query.filter_by(date_id=date.id, ccy_id=ccy.id).one()

        res = self.client().get(f'/curves/{curve.id}', headers={'Authorization':
                                                                'Bearer ' + self.test_client})

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['curve']['curve_id'], curve.id)
        self.assertEqual(data['curve']['spreads']['5Y'], 0.004313)

    @ insert_and_delete
    def test_post_new_curve_client(self):
        res = self.client().post('/curves', json={'ccy': 'USD',
                                                  'date': '20201230'}, headers={'Authorization':
                                                                                'Bearer ' + self.test_client})

        date_datetime = datetime.date(2020, 12, 30)
        ccy = Currency.query.filter_by(ccy='USD').one_or_none()
        date = Date.query.filter_by(date=date_datetime).one_or_none()
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)

    @ insert_and_delete
    def test_patch_curve_client(self):
        yyyymmdd = '20201231'
        currency = 'USD'
        date_datetime = to_datetime(yyyymmdd)

        ccy = Currency.query.filter_by(ccy=currency).one_or_none()
        date = Date.query.filter_by(date=date_datetime).one_or_none()

        curve = Curve.query.filter_by(date_id=date.id, ccy_id=ccy.id).one()

        res = self.client().patch(
            f'/curves/{curve.id}', json={'override': {'5Y': 0.002020}}, headers={'Authorization':
                                                                                 'Bearer ' + self.test_client})

        date = Date.query.filter_by(date=date_datetime).one_or_none()
        ccy = Currency.query.filter_by(ccy=currency).one_or_none()
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)

    @ insert_and_delete
    def test_delete_curve_client(self):
        yyyymmdd = '20201231'
        currency = 'USD'
        date_datetime = to_datetime(yyyymmdd)

        ccy = Currency.query.filter_by(ccy=currency).one_or_none()
        date = Date.query.filter_by(date=date_datetime).one_or_none()

        curve = Curve.query.filter_by(date_id=date.id, ccy_id=ccy.id).one()
        curve_id = curve.id
        res = self.client().delete(f'/curves/{curve_id}', json={'ccy': currency,
                                                                'date': yyyymmdd}, headers={'Authorization':
                                                                                            'Bearer ' + self.test_client})

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)

    '''
    Tests for quant role access
    '''
    @insert_and_delete
    def test_get_currencies(self):
        res = self.client().get('/currencies', headers={'Authorization':
                                                        'Bearer ' + self.test_quant})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(type(data['currencies']), dict)

    @insert_and_delete
    def test_get_dates(self):
        res = self.client().get('/dates', headers={'Authorization':
                                                   'Bearer ' + self.test_quant})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(type(data['dates']), dict)

    @ insert_and_delete
    def test_post_request_curve_id(self):
        date_datetime = datetime.date(2020, 12, 31)
        ccy = Currency.query.filter_by(ccy='USD').one_or_none()
        date = Date.query.filter_by(date=date_datetime).one_or_none()

        curve = Curve.query.filter_by(date_id=date.id, ccy_id=ccy.id).one()

        res = self.client().post('/curves/id', json={'ccy': 'USD',
                                                     'date': '20201231'}, headers={'Authorization':
                                                                                   'Bearer ' + self.test_quant})

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['curve_id'], curve.id)

    @ insert_and_delete
    def test_get_curve_by_id(self):
        date_datetime = datetime.date(2020, 12, 31)
        ccy = Currency.query.filter_by(ccy='USD').one_or_none()
        date = Date.query.filter_by(date=date_datetime).one_or_none()

        curve = Curve.query.filter_by(date_id=date.id, ccy_id=ccy.id).one()

        res = self.client().get(f'/curves/{curve.id}', headers={'Authorization':
                                                                'Bearer ' + self.test_quant})

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['curve']['curve_id'], curve.id)
        self.assertEqual(data['curve']['spreads']['5Y'], 0.004313)

    @ insert_and_delete
    def test_post_new_curve(self):
        res = self.client().post('/curves', json={'ccy': 'USD',
                                                  'date': '20201230'}, headers={'Authorization':
                                                                                'Bearer ' + self.test_quant})

        date_datetime = datetime.date(2020, 12, 30)
        ccy = Currency.query.filter_by(ccy='USD').one_or_none()
        date = Date.query.filter_by(date=date_datetime).one_or_none()
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['curve']['ccy_id'], ccy.id)
        self.assertEqual(data['curve']['date_id'], date.id)
        self.assertEqual(data['spread'], 0.004357)

    @ insert_and_delete
    def test_patch_curve(self):
        yyyymmdd = '20201231'
        currency = 'USD'
        date_datetime = to_datetime(yyyymmdd)

        ccy = Currency.query.filter_by(ccy=currency).one_or_none()
        date = Date.query.filter_by(date=date_datetime).one_or_none()

        curve = Curve.query.filter_by(date_id=date.id, ccy_id=ccy.id).one()

        res = self.client().patch(
            f'/curves/{curve.id}', json={'override': {'5Y': 0.002020}}, headers={'Authorization':
                                                                                 'Bearer ' + self.test_quant})

        date = Date.query.filter_by(date=date_datetime).one_or_none()
        ccy = Currency.query.filter_by(ccy=currency).one_or_none()
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['curve']['ccy_id'], ccy.id)
        self.assertEqual(data['curve']['date_id'], date.id)
        self.assertEqual(data['spreads'], {'5Y': 0.002020})

    @ insert_and_delete
    def test_delete_curve(self):
        yyyymmdd = '20201231'
        currency = 'USD'
        date_datetime = to_datetime(yyyymmdd)

        ccy = Currency.query.filter_by(ccy=currency).one_or_none()
        date = Date.query.filter_by(date=date_datetime).one_or_none()

        curve = Curve.query.filter_by(date_id=date.id, ccy_id=ccy.id).one()
        curve_id = curve.id
        res = self.client().delete(f'/curves/{curve_id}', json={'ccy': currency,
                                                                'date': yyyymmdd}, headers={'Authorization':
                                                                                            'Bearer ' + self.test_quant})

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['deleted_curve_id'], curve_id)
        self.assertEqual(data['success'], True)


if __name__ == "__main__":
    unittest.main()
