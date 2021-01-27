import os
from sqlalchemy import Column, String, Integer, Date, Float, ForeignKey
from sqlalchemy.schema import UniqueConstraint, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.ext.declarative import declared_attr


db_user = os.environ.get('DB_USER')
db_password = os.environ.get('DB_PASS')

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
    # db.create_all()
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
    curves = relationship('Curve', backref='date',
                          cascade="all, delete-orphan", lazy=True)

    def __init__(self, date):
        self.date = date


class Currency(Generic, db.Model):

    ccy = Column(String, unique=True)
    curves = relationship('Curve', backref='currency',
                          cascade="all, delete-orphan", lazy=True)

    def __init__(self, ccy):
        self.ccy = ccy


class Tenor(Generic, db.Model):

    tenor = Column(String, unique=True)
    spreads = relationship('Spread', backref='tenor',
                           cascade="all, delete-orphan", lazy=True)

    def __init__(self, tenor):
        self.tenor = tenor


class Curve(Generic, db.Model):

    date_id = Column(Integer, ForeignKey('Date.id'), nullable=False)
    ccy_id = Column(Integer, ForeignKey(
        'Currency.id'), nullable=False)
    spreads = relationship('Spread', backref='curve',
                           cascade="all, delete-orphan", lazy=True)

    __table_args__ = (UniqueConstraint(
        'date_id', 'ccy_id', name='_curve_uc'), PrimaryKeyConstraint("id", name="_pk_id"),)

    def __init__(self, date_id, ccy_id):
        self.date_id = date_id
        self.ccy_id = ccy_id


class Spread(Generic, db.Model):

    tenor_id = Column(Integer, ForeignKey('Tenor.id'), nullable=False)
    curve_id = Column(Integer, ForeignKey('Curve.id'), nullable=False)
    spread = Column(Float)

    def __init__(self, tenor_id, curve_id,  spread):
        self.tenor_id = tenor_id
        self.curve_id = curve_id
        self.spread = spread
