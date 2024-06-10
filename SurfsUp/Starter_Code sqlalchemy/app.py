# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy as sql
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(autoload_with=engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    return (
        f"Welcome to the Climate App API!<br/><br/><br>"
        f"Available Routes:<br/><br>"
        f"Precipitation: /api/v1.0/precipitation<br/><br>"
        f"Stations: /api/v1.0/stations<br/><br>"
        f"Tobs: /api/v1.0/tobs<br/><br>"
        f"Temp Metrics since start = YYYY-MM-DD: /api/v1.0/&lt;start&gt;<br/><br>"
        f"Temp Metrics from start= YYYY-MM-DD to end=YYYY-MM-DD: /api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    one_year_ago = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()
    session.close()
    precipitation_data = {date: prcp for date, prcp in results}
    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station, Station.name).all()
    session.close()
    station_list = [{'station': result[0], 'name': result[1]} for result in results]
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    one_year_ago = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= one_year_ago)\
                                                            .filter(Measurement.station == 'USC00519281').all()
    session.close()
    temperature_observations = [{'date': date, 'tobs': tobs} for date, tobs in results]
    return jsonify(temperature_observations)

@app.route("/api/v1.0/<start>")
def start_date_stats(start):
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
                    .filter(Measurement.date >= start).all()
    session.close()
    temperature_stats = {'TMIN': results[0][0], 'TAVG': results[0][1], 'TMAX': results[0][2]}
    return jsonify(temperature_stats)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date_stats(start, end):
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    end_date = dt.datetime.strptime(end, '%Y-%m-%d')
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
                    .filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    session.close()
    temperature_stats = {'TMIN': results[0][0], 'TAVG': results[0][1], 'TMAX': results[0][2]}
    return jsonify(temperature_stats)

if __name__ == '__main__':
    app.run(debug=True)
