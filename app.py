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
def welcome():
    return """<html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta http-equiv="X-UA-Compatible" content="IE=edge">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Precipitation API</title>
                <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
                <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>
        </head>
            <h5 class="display-5">Welcome to our website, here is a list of all available routes</h5>
            <ul class="list-group">
                <br>
                <li class="list-group-item">
                    This API returns a list of precipitations from last year:
                    <br>
                    <a href="/api/v1.0/precipitation">/api/v1.0/precipitation</a>
                </li>
                <br>
                <li class="list-group-item">
                    This API returns a JSON list of stations from the dataset:
                    <br>
                    <a href="/api/v1.0/stations">/api/v1.0/stations</a>
                </li>
                <br>
                <li class="list-group-item">
                    This API returns a JSON list of Temperature Observations (tobs) for the previous year:
                    <br>
                    <a href="/api/v1.0/tobs">/api/v1.0/tobs</a>
                </li>
                <br>
                <li class="list-group-item">
                    This API returns a JSON list of tmin, tmax, tavg for the dates greater than or equal to the date provided:
                    <br>Please replace &ltstart&gt with a date in Year-Month-Day format.
                    <br>
                    <a href="/api/v1.0/2017-07-01">/api/v1.0/2017-07-14</a>
                </li>
                <br>
                <li class="list-group-item">
                    This API returns a JSON list of tmin, tmax, tavg for the dates in range of start date and end date inclusive:
                    <br>
                    Please replace &ltstart&gt and &ltend&gt with a date in Year-Month-Day format.
                    <br>
                    <br>
                    <a href="/api/v1.0/2017-07-01/2017-07-14">/api/v1.0/2017-07-01/2017-07-14</a>
                </li>
                <br>
            </ul>
            </html>
            """


@app.route("/api/v1.0/precipitation")
def precipitation():
    max_date = session.query(Measurement.date).order_by(
        Measurement.date.desc()).first()

    max_date = max_date[0]

    last_year = dt.datetime.strptime(
        max_date, "%Y-%m-%d") - dt.timedelta(days=365)

    precipitation_data = session.query(Measurement.date, Measurement.prcp).filter(
        Measurement.date >= last_year).all()

    precipitation_dict = dict(precipitation_data)

    return jsonify(precipitation_dict)


@app.route("/api/v1.0/stations")
def stations():
    stations_data = session.query(
        Measurement.station).group_by(Measurement.station).all()

    station_list = list(np.ravel(stations_data))

    return jsonify(station_list)


@app.route("/api/v1.0/tobs")
def tobs():
    max_date = session.query(Measurement.date).order_by(
        Measurement.date.desc()).first()

    max_date = max_date[0]

    last_year = dt.datetime.strptime(
        max_date, "%Y-%m-%d") - dt.timedelta(days=366)

    tobs_data = session.query(Measurement.date, Measurement.tobs).filter(
        Measurement.date >= last_year).all()

    tobs_list = list(np.ravel(tobs_data))

    return jsonify(tobs_list)


@app.route("/api/v1.0/<start>")
def start(start=None):
    from_start = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(
        Measurement.tobs)).filter(Measurement.date >= start).group_by(Measurement.date).all()

    from_start_list = list(np.ravel(from_start))

    return jsonify(from_start_list)


@app.route("/api/v1.0/<start>/<end>")
def start_end(start=None, end=None):
    between_dates = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(
        Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).all()

    between_dates_list = list(np.ravel(between_dates))

    return jsonify(between_dates_list)


if __name__ == "__main__":
    app.run(debug=True)
