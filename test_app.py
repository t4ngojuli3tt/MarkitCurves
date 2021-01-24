import unittest
import json
import datetime
from flask_migrate import downgrade, upgrade
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

from app import create_app, commit_ccy, commit_tenors
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

    def tearDown(self):
        """Executed after reach test"""
        self.db.session.remove()

    def test_get_currencies(self):
        commit_tenors()
        commit_ccy()
        res = self.client().get('/currencies')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(type(data['currencies']), dict)

    def test_get_dates(self):
        date_datetime = datetime.date(2020, 12, 30)
        Date(date_datetime).insert()
        res = self.client().get('/dates')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(type(data['dates']), dict)

        Date(date_datetime).delete()

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

    def test_delete_curve(self):
        self.client().post('/curves', json={'ccy': 'USD', 'date': '20201230'})

        res = self.client().delete('/curves', json={'ccy': 'USD',
                                                    'date': '20201230'})
        date_datetime = datetime.date(2020, 12, 30)
        ccy = Currency.query.filter_by(ccy='USD').one_or_none()
        date = Date.query.filter_by(date=date_datetime).one_or_none()
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['curve']['ccy_id'], ccy.id)
        self.assertEqual(data['curve']['date_id'], date.id)
        self.assertEqual(data['success'], True)


if __name__ == "__main__":
    unittest.main()
