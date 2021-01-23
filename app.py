import os
from flask import Flask, request, abort, jsonify, render_template, abort
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from models import setup_db


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    cors = CORS(app)
    return app


app = create_app()
