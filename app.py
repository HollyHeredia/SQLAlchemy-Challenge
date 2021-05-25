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
station = Base.classes.station
measurement = Base.classes.measurement

# Flask Setup
app = Flask(__name__)

# Flask Routes
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start>/<end>"
    )
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of station data including station, the name"""
    # Query all station
    results = session.query(station.station, station.name).all()

    session.close()

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
    session = Session(engine)

    """Return a list of passenger data including the name, age, and sex of each passenger"""
    # Query all passengers
    results = session.query(measurement.date, measurement.prcp).all()

    session.close()

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
    session = Session(engine)

    active_stations_descending = session.query(measurement.station, func.count(measurement.station)).\
                group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()

    most_active_station = active_stations_descending[0][0]

    stationsummary = session.query(measurement.station, measurement.date, measurement.tobs).\
        filter(measurement.station == most_active_station).all()

    last_date = session.query(measurement.date).order_by(measurement.date.desc()).first().date
    last_year = dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)

    temp_results = session.query(measurement.date, measurement.tobs).\
        filter(measurement.station == most_active_station).filter(measurement.date >= last_year).\
        group_by(measurement.date).all()

        

    print(f"For temperatures for the last year of station {most_active_station}:")
    return jsonify(temp_results)



# Return a JSON list of temperature observations (TOBS) for the previous year.

#@app.route("/api/v1.0/<start>")
#@app.route("/api/v1.0/<start>/<end>")

#Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.

# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.

if __name__ == '__main__':
    app.run(debug=True)
