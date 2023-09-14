# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt
from datetime import timedelta

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify



#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
base = automap_base()

# reflect the tables
base.prepare(autoload_with = engine)

# Save references to each table
Measurement = base.classes.measurement
Station = base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)



#################################################
# Flask Setup
#################################################

app = Flask(__name__)



#################################################
# Flask Routes
#################################################

## Start at homepage and list all available routes

@app.route("/")

def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )




## Convert the query results from your precipitation analysis to 
## dictionary using date as the key and prcp as the value.
## Return JSON representation of dictionary
    
@app.route("/api/v1.0/precipitation")

def precipitation():
    
    session=Session(engine)
    
    most_recent = session.query(func.max(Measurement.date)).first()
    
    year_back = dt.date(2017,8,23)-dt.timedelta(days=365)
    
    precipitation = session.query(Measurement.date,Measurement.prcp).\
    filter(Measurement.date >= year_back).all()
    
    session.close()
    
    all_precip = []
    for date, prcp in precipitation:
        precip_dict = {}
        precip_dict[date] = prcp
        all_precip.append(precip_dict)
    
    return jsonify(all_precip)




## Return a JSON list of stations

@app.route("/api/v1.0/stations")

def stations():
    
    session=Session(engine)
    
    stations = session.query(Station.station).all()
    
    session.close()
    
    station_list = list(np.ravel(stations))
    
    return jsonify(station_list)
    



## Query the dates and temperature observations of the most-active station 
## for the previous year of data.  Return a JSON list of temperature observations.

@app.route("/api/v1.0/tobs")

def tobs():
    
    session=Session(engine)
    
    most_active = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()[0]
    
    most_recent_active = session.query(func.max(Measurement.date).\
        filter(Measurement.station == most_active)).first()
    
    year_back_active = dt.date(2017,8,23)-dt.timedelta(days=365)
    
    data_temp_active = session.query(Measurement.tobs).\
        filter(Measurement.station == most_active).\
        filter(Measurement.date >= year_back_active).\
        all()
    
    session.close()
    
    tobs_list = list(np.ravel(data_temp_active))
    
    return jsonify(tobs_list)



## Return a JSON list of the minimum temperature, the average temperature, 
## and the maximum temperature for a specified start range

@app.route("/api/v1.0/<start>")

def start_temp(start):
    
    session=Session(engine)
    
    start_min_temp = session.query(func.min(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        all()
        
    start_max_temp = session.query(func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        all()
    
    start_avg_temp = session.query(func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        all()
    
    session.close()
    
#    temp_stats = []
    start_temp_stats = {}
    start_temp_stats["TMIN"] = start_min_temp
    start_temp_stats["TMAX"] = start_max_temp
    start_temp_stats["TAVG"] = start_avg_temp
 #   temp_stats.append(temp_stats_dict)
    
    return jsonify(start_temp_stats)




## Return a JSON list of the minimum temperature, the average temperature, 
## and the maximum temperature for a specified start range

@app.route("/api/v1.0/<start>/<end>")

def start_temp(start, end):
    
    session=Session(engine)
    
    se_min_temp = session.query(func.min(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).\
        all()
        
    se_max_temp = session.query(func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).\
        all()
    
    se_avg_temp = session.query(func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).\
        all()
    
    session.close()
    
#    temp_stats = []
    se_temp_stats = {}
    se_temp_stats["TMIN"] = se_min_temp
    se_temp_stats["TMAX"] = se_max_temp
    se_temp_stats["TAVG"] = se_avg_temp
 #   temp_stats.append(temp_stats_dict)
    
    return jsonify(se_temp_stats)



if __name__ == '__main__':
    app.run(debug=True)    