import os
from sqlalchemy import Column, String, Integer, Date, Float, create_engine
from sqlalchemy.schema import UniqueConstraint, PrimaryKeyConstraint
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.ext.declarative import declared_attr
#from sqlalchemy.sql.sqltypes import Float


db_user = 'postgres'  # os.environ.get('DB_USER')
db_password = 'postgres'  # os.environ.get('DB_PASS')

db_host = "localhost:5432"
db_name = "markit"

db_path = f'postgresql://{db_user}:{db_password}@{db_host}/{db_name}'

db = SQLAlchemy()


'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''


def setup_db(app, database_path=db_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    Migrate(app, db)


'''
Classes:
Date
Currency
Tenor
Curve
Spread
'''


class Generic():
    @declared_attr
    def __tablename__(cls):
        return cls.__name__

    id = Column(Integer, primary_key=True)

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Date(Generic, db.Model):

    date = Column(Date, unique=True)
    curves = db.relationship('Curve', backref='tenor', lazy=True)

    def __init__(self, date):
        self.date = date


class Currency(Generic, db.Model):

    ccy = Column(String, unique=True)
    curves = db.relationship('Curve', backref='tenor', lazy=True)

    def __init__(self, ccy):
        self.ccy = ccy


class Tenor(Generic, db.Model):

    tenor = Column(String, unique=True)
    spreads = db.relationship('Spread', backref='tenor', lazy=True)

    def __init__(self, tenor):
        self.tenor = tenor


class Curve(Generic, db.Model):

    date_id = db.Column(db.Integer, db.ForeignKey('Date.id'), nullable=False)
    ccy_id = db.Column(db.Integer, db.ForeignKey(
        'Currency.id'), nullable=False)
    spreads = db.relationship('Spread', backref='curve', lazy=True)

    __table_args__ = (UniqueConstraint(
        'date_id', 'ccy_id', name='_curve_uc'), PrimaryKeyConstraint("id", name="_pk_id"),)

    def __init__(self, date_id, ccy_id):
        self.date_id = date_id
        self.ccy_id = ccy_id


class Spread(Generic, db.Model):

    tenor_id = db.Column(db.Integer, db.ForeignKey('Tenor.id'), nullable=False)
    curve_id = db.Column(db.Integer, db.ForeignKey('Curve.id'), nullable=False)
    spread = Column(Float)

    curves = db.relationship('Curve', backref='tenor', lazy=True)

    def __init__(self, tenor_id, curve_id,  spread):
        self.tenor_id = tenor_id
        self.curve_id = curve_id
        self.spread = spread
