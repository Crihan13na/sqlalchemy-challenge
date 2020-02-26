import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite", echo=False)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save a reference to the measurenment table as 'Measurement'
Measurement = Base.classes.measurement
# Save a reference to the station table as 'Station'
Station = Base.classes.station
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
    #List all available api routes.
    return (
        "Hawaii Precipitation and Weather Data<br/><br/>"
    
        "Precipiation from 2016-08-23 to 2017-08-23.<br/>"
        "/api/v1.0/precipitation<br/><br/>"
        "Return a JSON list of stations from the dataset.<br/>"
        "/api/v1.0/stations<br/><br/>"
        "Return a JSON list of Temperature Observations (tobs) for the previous year.<br/>"
        "/api/v1.0/tobs<br/><br/>"
        "Return a JSON list of Tmax,Tmin,Tavg, given the start date only.<br/>"
        "/api/v1.0/temp/<start><br/><br/>"
        "Return a JSON list of Tmax,Tmin,Tavg, given the start and end date .<br/>"
        "/api/v1.0/temp/<start>/<end><br/>"
    )


#ast_12_months= dt.date(2017,8,23) - dt.timedelta(days=365)

@app.route("/api/v1.0/precipitation")
def precipitation():
    last_12_months = dt.date(2017,8,23) - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.prcp).\
              filter(Measurement.date > last_12_months).\
              order_by(Measurement.date).all()

     #Create a dictionary from the row data and add to a list of precipitation
    precip_data = []

    for precip in results:
        precip_dictionary = {}
        precip_dictionary["Date"]=precip.date
        precip_dictionary["Precipitation"] = precip.prcp
        precip_data.append(precip_dictionary)

    return jsonify(precip_data)
       
@app.route("/api/v1.0/stations")
def stations():
    #Query all the stations
    results = session.query(Station).all
    #create a dictionary from the row data and append to a list of stations.
    stations = []
    for station in results:
       stations_dictionary = {}
       stations_dictionary["Station"] = station.station
       stations_dictionary["Station Name"] = station.name
       stations_dictionary["Latitude"] = station.latitude
       stations_dictionary["Longitude"] = station.longitude
       stations_dictionary["Elevation"] = station.elevation 
       stations.append(stations_dictionary)
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    last_12_months = dt.date(2017,8,23) - dt.timedelta(days=365)
    #Query all the stations and for the given date
    results = session.query(Measurement.station,Measurement.date,Measurement.tobs).\
               group_by(Measurement.date).\
               filter(Measurement.date > last_12_months).\
               order_by(Measurement.date).all()

    # Create a dictionary from the row data and append is for the temperature data.
    temperature = []
    for temp_tobs in results:
        temp_dictionary = {}
        temp_dictionary["Station"]= temp_tobs.station
        temp_dictionary["Date"]= temp_tobs.date
        temp_dictionary["Temperature"]= temp_tobs.tobs
        temperature.append(temp_dictionary)

    return jsonify(temperature)

@app.route("/api/v1.0/<start>")
def start(start=None):
    #Query all the stations and for the given date.
    results = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date >= start).all()
        
    temp_start = []
    for TMIN, TMAX, TAVG in results:
        temp_start_dictionary = {}
        temp_start_dictionary["Minimum Temp"] = TMIN
        temp_start_dictionary["Maximum Temp"] = TMAX
        temp_start_dictionary["Average Temp"] = TAVG
        temp_start.append(temp_start_dictionary)
    return jsonify(temp_start)

@app.route("/api.v1.0/<start>/<end>")
def start_end(start=None, end=None):
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date >= start_date).\
    filter(Measurement.date <= end_date).all()

    start_end_temp = []
    for TMIN, TMAX, TAVG in results:
        start_end_temp_dictionary = {}
        start_end_temp_dictionary["Minimum Temp"] = TMIN
        start_end_temp_dictionary["Maximum Temp"] = TMAX
        start_end_temp_dictionary["Average Temp"] = TAVG
        start_end_temp.append(start_end_temp_dictionary)
    return jsonify(start_end_temp)

if __name__ == '__main__':
    app.run(debug=True)
