import numpy as np

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt


# Initialaizing Database
engine = create_engine("sqlite:///Resources/hawaii.sqlite",
                       connect_args={'check_same_thread': False}, echo=True)

Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

# Initialaizing Flask
app = Flask(__name__)


# Routes
@app.route("/")
def home():
    return (f"Available Routes:<br/>"
            f"/api/v1.0/precipitation<br/>"
            f"/api/v1.0/stations<br/>"
            f"/api/v1.0/tobs<br/>"
            f"/api/v1.0/start<br/>"
            f"/api/v1.0/start/end<br/>")



@app.route("/api/v1.0/precipitation")
def precipitation():

     # Create our session (link) from Python to the DB.
    session = Session(engine)

    max_date = session.query(Measurement.date).order_by(
        Measurement.date.desc()).first()

    max_date = max_date[0]

    last_year = dt.datetime.strptime(
        max_date, "%Y-%m-%d") - dt.timedelta(days=365)

    precipitation_data = session.query(Measurement.date, Measurement.prcp).filter(
        Measurement.date >= last_year).all()

    session.close()

    # Convert the query results to a dictionary
    precipitation_list = []
    for date, prcp in precipitation_data:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        precipitation_list.append(precipitation_dict)    

    precipitation_dict = dict(precipitation_data)

    return jsonify(precipitation_dict)


@app.route("/api/v1.0/stations")
def stations():

    session = Session(engine)

    stations_data = session.query(Station.station, Station.name,\
                                            Station.latitude, Station.longitude,\
                                            Station.elevation).all()

    session.close()                                        


    stations_list = []
    for station, name, latitude, longitude, elevation in stations_data:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        station_dict["latitude"] = latitude
        station_dict["longitude"] = longitude
        station_dict["elevation"] = elevation
        stations_list.append(station_dict)

    return jsonify(stations_list)


@app.route("/api/v1.0/tobs")
def tobs():

    session = Session(engine)

    max_date = session.query(Measurement.date).order_by(
        Measurement.date.desc()).first()

    max_date = max_date[0]

    last_year = dt.datetime.strptime(
        max_date, "%Y-%m-%d") - dt.timedelta(days=366)

    tobs_data = session.query(Measurement.date, Measurement.tobs).filter(
        Measurement.date >= last_year).all()

    session.close()

    tobs_list = []
    for date, temp in tobs_data:
        if temp != None:
           temp_dict = {}
           temp_dict["date"] = date
           temp_dict["temp"] = temp
           tobs_list.append(temp_dict)

    return jsonify(tobs_list)


@app.route("/api/v1.0/<start>")
def start(start=None):

    session=Session(engine)

    from_start = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(
        Measurement.tobs)).filter(Measurement.date >= start).group_by(Measurement.date).all()

    session.colse()

    temp_list = []
    for min, avg, max in from_start:
        temp_dict = {}
        temp_dict["Min"] = min
        temp_dict["Average"] = avg
        temp_dict["Max"] = max
        temp_list.append(temp_dict)

    return jsonify(temp_list)


@app.route("/api/v1.0/<start>/<end>")
def start_end(start=None, end=None):

    session=Session(engine)

    between_dates = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(
        Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).all()

    session.colse()

    temp_list = []
    for min, avg, max in between_dates:
        temp_dict = {}
        temp_dict["Min"] = min
        temp_dict["Average"] = avg
        temp_dict["Max"] = max
        temp_list.append(temp_dict)

    return jsonify(temp_list)


if __name__ == "__main__":
    app.run(debug=True)
