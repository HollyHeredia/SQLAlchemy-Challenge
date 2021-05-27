import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Station = Base.classes.station
measurement = Base.classes.measurement

session = Session(engine)

# Flask Setup
app = Flask(__name__)

# Flask Routes
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"List of Stations: /api/v1.0/stations<br/>"
        f"Temperature for one year: /api/v1.0/tobs<br/>"
        f"Temperature stat from the start date(yyyy-mm-dd): /api/v1.0/<yyyy-mm-dd><br/>"
        f"Temperature stat from start to end dates(yyyy-mm-dd): /api/v1.0/<yyyy-mm-dd>/<yyyy-mm-dd>"
    )
@app.route("/api/v1.0/stations")
def stations():
    """Return a list of station data including station, the name"""
    args=[(Station.station), (Station.name)]
    results = session.query(*args).all()

    # Create a dictionary from the row data and append to a list of all_stations
    all_stations = []
    for station, name in results:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        all_stations.append(station_dict)

    return jsonify(all_stations)

@app.route("/api/v1.0/precipitation")
def preciptations():
    # Create our session (link) from Python to the DB

    """Return a list of passenger data including the name, age, and sex of each passenger"""
    # Query all passengers
    results = session.query(measurement.date, measurement.prcp).all()

    # Create a dictionary from the row data and append to a list of all_preciptations
    all_precipitations = []
    for date, prcp in results:
        preciptation_dict = {}
        preciptation_dict["date"] = date
        preciptation_dict["prcp"] = prcp
        all_precipitations.append(preciptation_dict)

    return jsonify(all_precipitations)

@app.route("/api/v1.0/tobs")
# Query the dates and temperature observations of the most active station for the last year of data.
def tobs():
    args = [measurement.station, func.count(measurement.station)]
    active_stations_descending = session.query(*args).\
                group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()

    most_active_station = active_stations_descending[0][0]

    print(f"For temperatures for the last year of station: {most_active_station}")

    last_date = session.query(measurement.date).order_by(measurement.date.desc()).first().date
    last_year = dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)

    temp_results = session.query(measurement.date, measurement.tobs).\
        filter(measurement.station == most_active_station).filter(measurement.date >= last_year).\
        group_by(measurement.date).all()

    return jsonify(temp_results)


@app.route("/api/v1.0/<start>")
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
def get_start(start):
    args=[func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]
    results = session.query(*args).\
        filter(measurement.date >= start).all()

    tobsall = []
    for min,avg,max in results:
        tobs_dict = {}
        tobs_dict["Temp_Min"] = min
        tobs_dict["Temp_Average"] = avg
        tobs_dict["Temp_Max"] = max
        tobsall.append(tobs_dict)
    
    return jsonify(tobsall)

@app.route("/api/v1.0/<start>/<stop>")
# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.

def get_t_start_stop(start,stop):
    arg = [func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]
    results = session.query(*arg).\
        filter(measurement.date >= start).filter(measurement.date <= stop).all()

    tobsall = []
    for min,avg,max in results:
        tobs_dict = {}
        tobs_dict["Temp_Min"] = min
        tobs_dict["Temp_Average"] = avg
        tobs_dict["Temp_Max"] = max
        tobsall.append(tobs_dict)
    
    return jsonify(tobsall)


if __name__ == '__main__':
    app.run(debug=True)
