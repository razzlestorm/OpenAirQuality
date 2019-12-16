"""OpenAQ Air Quality Dashboard with Flask."""
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import openaq

APP = Flask(__name__)
APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
DB = SQLAlchemy(APP)
#DB.init_app(app)

@APP.route('/', methods=['GET'])
def root():
    risky = Record.query.filter(Record.value > 10).all()
    return render_template('base.html', title='Home', results=risky)


############ MODELS #############

class Record(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    datetime = DB.Column(DB.String(25), nullable=False)
    value = DB.Column(DB.Float, nullable=False)
    city = DB.Column(DB.String(30), nullable=False)
    country = DB.Column(DB.String(30), nullable=False)

    def __repr__(self):
        return f'<Time {self.datetime} --- {self.value}>'


@APP.route('/refresh', methods=['GET'])
def refresh():
    """Pull fresh data from Open AQ and replace existing data."""
    DB.drop_all()
    DB.create_all()
    api = openaq.OpenAQ()
    status, body = api.measurements(city='Atlantic City', country='US', parameter='pm25')
    results = body['results']
    for ii in range(len(results)):
        db_record = Record(id=ii, datetime=results[ii]['date']['utc'],
                        value=results[ii]['value'], city=results[ii]['city'],
                        country=results[ii]['country'])
        DB.session.add(db_record)
    DB.session.commit()
    return 'Data refreshed!'
