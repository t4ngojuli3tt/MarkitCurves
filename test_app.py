import unittest
import json
from flask_migrate import downgrade, upgrade
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

from app import create_app, commit_ccy, commit_tenors
from models import setup_db, db_user, db_password, db_host


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
            # create all tables
            upgrade()
            commit_ccy()
            commit_tenors()

    def tearDown(self):
        """Executed after reach test"""
        with self.app.app_context():
            downgrade()

    def test_get_currencies(self):
        res = self.client().get('/currencies')
        data = json.loads(res.data)
        print(data['currencies'])

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)


if __name__ == "__main__":
    unittest.main()
