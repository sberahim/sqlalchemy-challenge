import numpy as np
import datetime as dt
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#Flask Setup
app = Flask(__name__)

#Define Flask Routes
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
        f"Please use YYYY-mm-dd for both start and end date format to access the data"

    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(bind=engine)

    # Get the last 12 months date frm the recent date
    last_12_months = dt.date(2017,8,23) - dt.timedelta(days=365)

    # Query the prcp results and the date
    prcp_result = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date>=last_12_months).all()

    # Create a dataframe with date and precipitation column, store value from the query result and remove any row with NA result.
    prcp_df = pd.DataFrame(prcp_result, columns=['Date', 'Precipitation']).dropna()
    
    # Convert dataframe to dictionary
    prcp_dict = pd.Series(prcp_df.Precipitation.values, index=prcp_df.Date).to_dict()

    # Close the session
    session.close()

    #Return the JSON representation from the dictionary
    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(bind=engine)

    # Query the data for all stations
    stations = session.query(Station.id, Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()

    # Create a dataframe with date and precipitation column, store value from the query result and remove any row with NA result.
    station_df = pd.DataFrame(stations, columns=['ID', 'Station','Name','Latitude','Longitude','Elevation'])
    
    # Convert dataframe to dictionary
    station_dict = station_df.set_index('Station').T.to_dict('list')

    # Close the session
    session.close()

    #Return the JSON representation from the dictionary
    return jsonify(station_dict)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(bind=engine)

    # Get the last 12 months date frm the recent date
    last_12_months = dt.date(2017,8,18) - dt.timedelta(days=365)

    # Get the most active station name
    mostActiveStation = session.query(Measurement.station).group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).first()

    # Query the dates and temperature observations of the most-active station for the previous year
    tobs_result = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date>=last_12_months, Measurement.station == mostActiveStation[0]).all()

    # Create a dataframe with date and precipitation column, store value from the query result and remove any row with NA result.
    tobs_df = pd.DataFrame(tobs_result, columns=['Date', 'Temperature'])
    
    # Convert dataframe to dictionary
    tobs_dict = pd.Series(tobs_df.Temperature.values, index=tobs_df.Date).to_dict()

    # Close the session
    session.close()

    #Return the JSON representation from the dictionary
    return jsonify(tobs_dict)

@app.route("/api/v1.0/<start>")
def start(start):
    # Create our session (link) from Python to the DB
    session = Session(bind=engine)

    # Query the dates and temperature observations of the most-active station for the previous year
    start_tobs_result = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    # Store each min, avg and max into the dictionary
    for min, avg, max in start_tobs_result:
        start_tobs = {}
        start_tobs["min"] = min
        start_tobs["average"] = avg
        start_tobs["max"] = max

    # Close the session
    session.close()

    #Return the JSON representation from the dictionary
    return jsonify(start_tobs)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    # Create our session (link) from Python to the DB
    session = Session(bind=engine)

    # Query the dates and temperature observations of the most-active station for the previous year
    start_end_tobs_result = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
        filter(Measurement.date >= start, Measurement.date <= end).all()

    # Store each min, avg and max into the dictionary
    for min, avg, max in start_end_tobs_result:
        start_end_tobs = {}
        start_end_tobs["min"] = min
        start_end_tobs["average"] = avg
        start_end_tobs["max"] = max

    # Close the session
    session.close()

    #Return the JSON representation from the dictionary
    return jsonify(start_end_tobs)

if __name__ == '__main__':
    app.run(debug=True)