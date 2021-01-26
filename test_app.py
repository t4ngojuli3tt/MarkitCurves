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
        self.test_client = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkpmWGJjTGxrSXRwelhxUTVRc3pBSSJ9.eyJpc3MiOiJodHRwczovL3RvbWFzenRvbWFzei5ldS5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjAwZjE1NmZjZTI1ODkwMDcxOTY5Y2Q1IiwiYXVkIjoibWFya2l0IiwiaWF0IjoxNjExNjc1ODIyLCJleHAiOjE2MTE3NjIyMjIsImF6cCI6IkJtWHFyTzlpdEdmaEx5YmgzMHNDVUVIWkY5UjNQRm5RIiwic2NvcGUiOiIiLCJwZXJtaXNzaW9ucyI6WyJnZXQ6Y3VycmVuY3kiLCJnZXQ6Y3VydmUiLCJnZXQ6ZGF0ZSJdfQ.T1tIRR1483rIuEvxlYZYqDsQsetjDNsxn2YNzJyV7XesaM6rwNVd5IfXy6gtIwSwxByR8G285R-szG9ujS023vOMuAO1BFSVibow3XRBH6SH_uLf9OBD9D4KDtc9GzUfUsoSFiEVmCg5V960T3dukzvNHl46A4RZq4mVpQIBmNvetiITbKj39szhlUuj28bYnP2JIPlj0S5HlUB-ay5Mxt6T2SiimBFc-VN4IKSPd6uiOagzrlLRhValoI9ufy_6MkVuYXpAHkO7MFwcSHVVobapW2_50WmOV3Tiy8sXkVt5Scq3790XiFa2TqltGUVdrGIADCjLGMAr19h2Iiscjg"
        self.test_quant = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkpmWGJjTGxrSXRwelhxUTVRc3pBSSJ9.eyJpc3MiOiJodHRwczovL3RvbWFzenRvbWFzei5ldS5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjAwZjE1ZTgyMGFhMTcwMDZhYzcxM2EwIiwiYXVkIjoibWFya2l0IiwiaWF0IjoxNjExNjc3MjQ2LCJleHAiOjE2MTE3NjM2NDYsImF6cCI6IkJtWHFyTzlpdEdmaEx5YmgzMHNDVUVIWkY5UjNQRm5RIiwic2NvcGUiOiIiLCJwZXJtaXNzaW9ucyI6WyJkZWxldGU6Y3VydmUiLCJnZXQ6Y3VycmVuY3kiLCJnZXQ6Y3VydmUiLCJnZXQ6ZGF0ZSIsInBhdGNoOmN1cnZlIiwicG9zdDpjdXJ2ZSJdfQ.mC2clrZ-MrYiTIhAk9IjxV-ELaqrzZByp5tWuJXiTjwTT1f-X6ZtMEgYKP6pEhNB4mRFD2p7ckQ3NLcnCC1uFNL0-qZu-pcdoWJgHlViDYLqxJagdg_h73mxk_IdoOfhypQbHFaCiQNK41D4Pty5r7lPzDNglkJGdAky0YOMtPHmY5nzreW2bFS6cL2B4oH32d6ljw6hA_pELPEidFq6ZnGNV6P-L6snwppudTbv3HOUbys5ewaJ3a-E-ahHlEn1DLts0MdKETQgfs7PCl3wz5PU4djncJJFMO4jPMTGm1JKjBGSdOV8vpC3GapZ9R-2Nn9nrelNKlgSe6g3eiiu3g"
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
        self.assertEqual(data['spread'], 0.002020)

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
