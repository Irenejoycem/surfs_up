import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#access SQLite database
engine = create_engine("sqlite:///hawaii.sqlite")

#reflect the database into our classes
Base = automap_base()

#reflect the database
Base.prepare(engine, reflect=True)

#With the database reflected, we can save our references to each table, variables to reference later
Measurement = Base.classes.measurement
Station = Base.classes.station

#create a session link from Python to our database 
session = Session(engine)

#To define our Flask app, add the following line of code. This will create a Flask application called "app."
app = Flask(__name__)

#add welcome route
@app.route("/")

#create a function welcome() with a return statement
##When creating routes, we follow the naming convention /api/v1.0/ followed by the name of the route. 
def welcome():
    return(
    '''
    Welcome to the Climate Analysis API!
    Available Routes:
    /api/v1.0/precipitation
    /api/v1.0/stations
    /api/v1.0/tobs
    /api/v1.0/temp/start/end
    ''')

#create a new route, always align to the very left
@app.route("/api/v1.0/precipitation")

#create precipitation function
def precipitation():
    #add the line of code that calculates the date one year ago from the most recent date in the database
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    #write a query to get the date and precipitation for the previous year
    #tip: ".\" shortens the length of your query line so that it extends to the next line 
    precipitation = session.query(Measurement.date, Measurement.prcp).\
      filter(Measurement.date >= prev_year).all()
    #format our results into a JSON structured file
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)

#stations route
@app.route("/api/v1.0/stations")

#stations function
def stations():
    #create a query that will allow us to get all of the stations in our database
    results = session.query(Station.station).all()
    # unraveling our results into a one-dimensional array. 
    #To do this, we want to use thefunction np.ravel(), with results as our parameter.
    #To convert the results to a list, we will need to use the list function, which is list(), 
    #and then convert that array into a list
    #Then we'll jsonify the list and return it as JSON
    stations = list(np.ravel(results))
    return jsonify(stations=stations)

#temp route
@app.route("/api/v1.0/tobs")

def temp_monthly():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.tobs).\
      filter(Measurement.station == 'USC00519281').\
      filter(Measurement.date >= prev_year).all()
    temps = list(np.ravel(results))
    return jsonify(temps=temps)

#statistics route
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")

def stats(start=None, end=None):
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        results = session.query(*sel).\
            filter(Measurement.date >= start).\
            filter(Measurement.date <= end).all()
        temps = list(np.ravel(results))
        return jsonify(temps)

    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    temps = list(np.ravel(results))
    return jsonify(temps=temps)