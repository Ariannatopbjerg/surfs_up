#Dependencies
import datetime as dt
import numpy as np
import pandas as pd
#Dependencies for SQLAlchemy (help access our data in the SQLite database)
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
#Dependency for Flask
from flask import Flask, jsonify
#Setting up database engine for the Flask application
engine = create_engine("sqlite:///hawaii.sqlite")  # the creat_engine() function will allow us to access and query the SQLite database file
#Reflect the database into our classes
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
#create a variable for each of the classes for future reference 
Measurement = Base.classes.measurement
Station = Base.classes.station
# create a session link from Python to our database
session = Session(engine)

# Set up Flask
app = Flask(__name__)
# All routes should go after the above code; otherwise code may not run properly
# Define welcome route:
@app.route("/")
# Next: add routing info for each of the other routes. Create a function and return statement will have f-strings as a reference to all of the other routes pf the data.
def welcome():
    return(
    # add preceipiation, stations, tobs, and temp routes
    '''
    Welcome to the Climate Analysis API!
        Available Routes:
            /api/v1.0/precipitation
            /api/v1.0/stations
            /api/v1.0/tobs
            /api/v1.0/temp/start/end
    ''')
    # NOTE
    # When creating routes, we follow the naming convention /api/v1.0/ followed by the name of the route. 
    # This convention signifies that this is version 1 of our application. This line can be updated to support future versions of the app as well.

#Precipitation Route
@app.route("/api/v1.0/precipitation")
def precipitation():
    # want to add the line of code that calculates the date one year ago from the most recent date in the database. 
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # write a query to get the date and precipitation for the previous year.
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all()
    
    # Notice the .\ in the first line of our query? This is used to signify that we want our query to continue on the next line. 
    # You can use the combination of .\ to shorten the length of your query line so that it extends to the next line.                        

    # create a dictionary with the date as the key and the precipitation as the value. To do this, we will "jsonify" our dictionary.
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)

#Station Route
@app.route("/api/v1.0/stations")
def stations():
    # Create a query that will allow us to get all of the stations in our database
    results = session.query(Station.station).all()
    # Unravel our results into a one-dimensional array ->  use thefunction np.ravel(), with results as our parameter.
    # Then convert the unraveled results into a list -> use the list function, which is list(), and then convert that array into a list
    # Then jsonify the list and return it as JSON
    stations = list(np.ravel(results))
    return jsonify(stations=stations)

    # You may notice here that to return our list as JSON, we need to add stations=stations. This formats our list into JSON.

# Temperature Route
@app.route("/api/v1.0/tobs")
def temp_monthly():
    # Calculate the date one year ago from the last date in the database
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # query the primary station for all the temperature observations from the previous year
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()
    # unravel the results into a one-dimensional array and convert that array into a list and jsonify the list and return our results
    temps = list(np.ravel(results))
    return jsonify(temps=temps)


# Statistics Route
# Diff from other routes - provide both a starting and ending date
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
# add parameters to our stats()function: a start parameter and an end parameter
def stats(start=None, end=None):
    # creating a list called sel
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    # need to determine the starting and ending date, add an if-not statement. asterisk next to sel list is used to indicate there will be multiple results for our query: min, avg, and max temps.
    # calculate the temperature minimum, average, and maximum with the start and end dates. use the sel list, which is simply the data points we need to collect.
    # Query will retrieve stats data
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

# Need to specify a start and end date for the range. 
# i.e. /api/v1.0/temp/2017-06-01/2017-06-30 and use code: def stats(start='2017-06-01', end='2017-06-30'): 

if __name__ == '__main__':
    app.run(debug=True)

