import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

from app import create_app
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
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass
