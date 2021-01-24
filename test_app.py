import unittest
import json
import datetime
from flask_migrate import downgrade, upgrade
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

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

    @insert_and_delete
    def test_get_currencies(self):
        res = self.client().get('/currencies')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(type(data['currencies']), dict)

    @insert_and_delete
    def test_get_dates(self):
        res = self.client().get('/dates')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(type(data['dates']), dict)

    @insert_and_delete
    def test_post_curve(self):
        res = self.client().post('/curves', json={'ccy': 'USD',
                                                  'date': '20201230'})

        date_datetime = datetime.date(2020, 12, 30)
        ccy = Currency.query.filter_by(ccy='USD').one_or_none()
        date = Date.query.filter_by(date=date_datetime).one_or_none()
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['curve']['ccy_id'], ccy.id)
        self.assertEqual(data['curve']['date_id'], date.id)
        self.assertEqual(data['spread'], 0.004357)

    @insert_and_delete
    def test_patch_curve(self):
        currency = 'USD'
        yyyymmdd = '20201231'

        res = self.client().patch('/curves', json={'ccy': currency,
                                                   'date': yyyymmdd, 'override': {'5Y': 0.002020}})

        date = Date.query.filter_by(date=to_datetime(yyyymmdd)).one_or_none()
        ccy = Currency.query.filter_by(ccy=currency).one_or_none()
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['curve']['ccy_id'], ccy.id)
        self.assertEqual(data['curve']['date_id'], date.id)
        self.assertEqual(data['spread'], 0.002020)

    @insert_and_delete
    def test_delete_curve(self):
        currency = 'USD'
        yyyymmdd = '20201231'

        date_datetime = to_datetime(yyyymmdd)
        date = Date.query.filter_by(date=date_datetime).one_or_none()
        ccy = Currency.query.filter_by(ccy=currency).one_or_none()

        res = self.client().delete('/curves', json={'ccy': currency,
                                                    'date': yyyymmdd})

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['curve']['ccy_id'], ccy.id)
        self.assertEqual(data['curve']['date_id'], date.id)
        self.assertEqual(data['success'], True)


if __name__ == "__main__":
    unittest.main()
