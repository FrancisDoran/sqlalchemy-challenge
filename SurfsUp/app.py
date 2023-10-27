# Import the dependencies.
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify 
import datetime as dt

#################################################
# Database Setup
#################################################
engine=create_engine('sqlite:///Resources/hawaii.sqlite')

# reflect an existing database into a new model
base=automap_base()
# reflect the tables
base.prepare(autoload_with=engine)

# Save references to each table
measurement=base.classes.measurement
station=base.classes.station

# Create our session (link) from Python to the DB
session=Session(engine)

#################################################
# Flask Setup
#################################################
app=Flask(__name__)


most_recent=session.query(func.max(measurement.date)).first()[0]
year=int(most_recent[0:4])
month=int(most_recent[5:7])
day=int(most_recent[8:])
#################################################
# Flask Routes
#################################################
# guide to the api
@app.route('/')
def index():
    """Return the list of available API routes."""
    return (
        f'All availible routes are below<br/>'
        f'/api/v1.0/precipitation<br/>'
        f'/api/v1.0/stations<br/>'
        f'/api/v1.0/tobs<br/>'
        f'/api/v1.0/<start><br/>'
        f'/api/v1.0/<start>/<end><br/>'
        f'Have fun!'
    )
@app.route('/api/v1.0/precipitation')
def prcp():
    """Return precipitation data for the last year."""
    year_ago = dt.date(year,month,day) - dt.timedelta(days=365)
    past_year_data=session.query(measurement.prcp, measurement.date).filter(measurement.date >= year_ago).all()
    session.close()
    dic={}
    for row in past_year_data:
        dic[row[1]]=row[0]
    return jsonify(dic)
@app.route('/api/v1.0/stations')
def stations():
    """Return a list of all station names."""
    output=session.query(station.station).all()
    session.close()
    c=[]
    for row in output:
        c.append(row[0])
    return jsonify(c)
@app.route('/api/v1.0/tobs')
def tobs():
    """Return temperature observations for the most frequent station."""
    most_frequent=session.query(measurement.station,func.count(measurement.station)).group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()[0][0]
    data=session.query(measurement.date,measurement.tobs).where(measurement.station ==most_frequent).all()
    dic={}
    for row in data:
        dic[row[1]]=row[0]
    return jsonify(dic)
@app.route('/api/v1.0/<start>') 
@app.route('/api/v1.0/<start>/<end>')
def temp(start=None,end=None):
    """Return TMIN, TAVG, and TMAX for a given time range."""
    default=session.query(func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs))
    try:
        if start:
            default=default.where(measurement.date >= start)
        if end: 
            default=default.where(measurement.date <= end)
        default=default.all()[0]
        dic={}
        dic['TMIN']=default[0]
        dic['TMAX']=default[1]
        dic['TAVG']=default[2]
        return jsonify(dic)
    except:
        return jsonify({"error": 'Please enter dates as strings in "YYYY-MM-DD" format'}), 400 
