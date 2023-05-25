# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

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
def welcome():
    """List all available api routes."""
    return (
        "Welcome to the home page!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

####################################################################
@app.route("/api/v1.0/precipitation")
def precipitation():
#query the 12 month precipitation analysis from "climate_starter_real.ipynb"

    # Find the most recent date in the data set.
    recent_date_str = session.query(func.max(measurement.date)).scalar()
    #convert back to date object
    recent_date = dt.datetime.strptime(recent_date_str, "%Y-%m-%d").date()
    #find the old date and end the session
    oldDate = recent_date - dt.timedelta(days=365)
    session.close()

    twelveMonths = session.query(measurement.date, measurement.prcp).\
    filter(measurement.date >= oldDate).all()
    session.close()

    precip_list = []
    for date, prcp in twelveMonths:
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["prcp"] = prcp
        precip_list.append(precip_dict)
    return jsonify(precip_list)

####################################################################
@app.route("/api/v1.0/stations")
def stations():
    station_query = session.query(station.station, station.name, station.latitude,
                                station.longitude, station.elevation).all()
    session.close()

    station_list = []
    for stat, name, lat, lon, elev in station_query:
        station_dict = {}
        station_dict["station"] = stat
        station_dict["name"] = name
        station_dict["latitude"] = lat
        station_dict["longitude"] = lon
        station_dict["elevation"] = elev
        station_list.append(station_dict)
    return jsonify(station_list)

####################################################################
@app.route("/api/v1.0/tobs")
def tobs():
    recent_station_date_str = session.query(func.max(measurement.date)).\
        filter(measurement.station == "USC00519281").\
        scalar()
    recent_station_date = dt.datetime.strptime(recent_station_date_str, "%Y-%m-%d").date()
    old_station_date = recent_station_date - dt.timedelta(days=365)
    session.close()

    twelveMonthsStation = session.query(measurement.date, measurement.tobs).\
        filter(measurement.date >= old_station_date).all()
    session.close()

    tobs_list = []
    for date, tobs in twelveMonthsStation:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_list.append(tobs_dict)
    return jsonify(tobs_list)

####################################################################
@app.route("/api/v1.0/<start>")
def temperature_stats(start):
        # Query the database to calculate temperature statistics
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).all()
    session.close()

    # Create a dictionary to store the temperature statistics
    temp_list = []
    for min_temp, max_temp, avg_temp in results:
        temp_dict = {}
        temp_dict["min"] = min_temp
        temp_dict["max"] = max_temp
        temp_dict["avg"] = avg_temp
        temp_list.append(temp_dict)
    return jsonify(temp_list)

####################################################################
@app.route("/api/v1.0/<start>/<end>")
def temperature_start_end(start, end):
        # Query the database to calculate temperature statistics
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).filter(measurement.date >= end).all()
    session.close()

    # Create a dictionary to store the temperature statistics
    temp_list = []
    for min_temp, max_temp, avg_temp in results:
        temp_dict = {}
        temp_dict["min"] = min_temp
        temp_dict["max"] = max_temp
        temp_dict["avg"] = avg_temp
        temp_list.append(temp_dict)
    return jsonify(temp_list)

####################################################################
if __name__ == "__main__":
    app.run(debug=True)

