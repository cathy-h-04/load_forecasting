import os
import uuid
import time

# #To-DO:
# stylistic edits:
# - rename the labels so they are more descriptive and legible. 
# - move the legend to the bottom


# 3) Finish coding the visualizations page. 
# 4) Figure out how to fix the maximum hourly change 

#importing sqlite3 for database use
import sqlite3
from sqlite3 import Error

# Importing flask for testing
from flask import Flask, flash, redirect, render_template, request, session, g, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from tempfile import mkdtemp
import json
import pandas as pd
import traceback

# Importing requests
from pip._vendor import requests

from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, func
from sqlalchemy.orm import relationship

# Import plotly and other necessary libraries
import plotly
from plotly.subplots import make_subplots
import plotly.graph_objs as go
import plotly.express as px

# Configure application
app = Flask(__name__)
app.secret_key = 'iLdWtWs365$'

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Replace 'your_database_url' with the actual database URL
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///load_forecasts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Users(db.Model):
    __tablename__ = "users"
    user_num = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String)
    ev_pt = Column(Float)
    pv_pt = Column(Float)
    hp_pt = Column(Float)

    calculated_loads = relationship("CalculatedLoads", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return (f"User(user_num={self.user_num!r}, user_id={self.user_id!r}, ev_pt={self.ev_pt!r}, "
                f"pv_pt={self.pv_pt!r}, hp_pt={self.hp_pt!r}, )")

class Loads(db.Model):
    __tablename__ = "loads"
    record_id = Column(Integer, primary_key=True, autoincrement=True)
    hour = Column(DateTime)
    base_central = Column(Float)
    base_south = Column(Float)
    base_north = Column(Float)
    ev_central = Column(Float)
    ev_south = Column(Float)
    ev_north = Column(Float)
    hp_central = Column(Float)
    hp_south = Column(Float)
    hp_north = Column(Float)
    pv_central = Column(Float)
    pv_south = Column(Float)
    pv_north = Column(Float)
    central_total = Column(Float)
    south_total = Column(Float)
    north_total = Column(Float)
    central_total_pv = Column(Float)
    south_total_pv = Column(Float)
    north_total_pv = Column(Float)
    no_pv_total = Column(Float)
    grand_total = Column(Float)

    def __repr__(self):
        return (f"Loads(record_id={self.record_id!r}, hour={self.hour!r}, "
                f"ev_central={self.ev_central!r}, ev_south={self.ev_south!r}, ev_north={self.ev_north!r}, "
                f"base_central={self.base_central!r}, base_south={self.base_south!r}, base_north={self.base_north!r}, "
                f"hp_central={self.hp_central!r}, hp_south={self.hp_south!r}, hp_north={self.hp_north!r}, "
                f"central_total={self.central_total!r}, south_total={self.south_total!r}, north_total={self.north_total!r}, "
                f"no_pv_total={self.no_pv_total!r}, grand_total={self.grand_total!r})")
    
class CalculatedLoads(db.Model):
    __tablename__ = "calculated_loads"
    record_id = Column(Integer, primary_key=True, autoincrement=True)
    hour = Column(DateTime)
    base_central = Column(Float)
    base_south = Column(Float)
    base_north = Column(Float)
    ev_central = Column(Float)
    ev_south = Column(Float)
    ev_north = Column(Float)
    hp_central = Column(Float)
    hp_south = Column(Float)
    hp_north = Column(Float)
    pv_central = Column(Float)
    pv_south = Column(Float)
    pv_north = Column(Float)
    central_total = Column(Float)
    south_total = Column(Float)
    north_total = Column(Float)
    central_total_pv = Column(Float)
    south_total_pv = Column(Float)
    north_total_pv = Column(Float)
    no_pv_total = Column(Float)
    grand_total = Column(Float)


    user_id = Column(String, ForeignKey('users.user_id'))

    user = relationship('Users', back_populates='calculated_loads')
    
    def __repr__(self):
        return (f"Loads(record_id={self.record_id!r}, hour={self.hour!r}, "
                f"ev_central={self.ev_central!r}, ev_south={self.ev_south!r}, ev_north={self.ev_north!r}, "
                f"base_central={self.base_central!r}, base_south={self.base_south!r}, base_north={self.base_north!r}, "
                f"hp_central={self.hp_central!r}, hp_south={self.hp_south!r}, hp_north={self.hp_north!r}, "
                f"central_total={self.central_total!r}, south_total={self.south_total!r}, north_total={self.north_total!r}, "
                f"no_pv_total={self.no_pv_total!r}, grand_total={self.grand_total!r}), user_id={self.user_id!r}")

def import_data(file_path, sheet_name):
    df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl')
    df.dropna(inplace=True)

    # Loop through the rows and insert data into the database
    for _, row in df.iterrows():
        load_data = Loads(
            hour=row['hour'],
            base_central=row['base_central'],
            base_south=row['base_south'],
            base_north=row['base_north'],
            ev_central=row['ev_central'],
            ev_south=row['ev_south'],
            ev_north=row['ev_north'],
            hp_central=row['hp_central'],
            hp_south=row['hp_south'],
            hp_north=row['hp_north'],
            pv_central=row['pv_central'],
            pv_south=row['pv_south'],
            pv_north=row['pv_north'],
            central_total=row['central_total'],
            south_total=row['south_total'],
            north_total=row['north_total'],
            central_total_pv=row['central_total_pv'],
            south_total_pv=row['south_total_pv'],
            north_total_pv=row['north_total_pv'],
            no_pv_total=row['no_pv_total'],
            grand_total=row['grand_total'])

        # Add the data to the session to be committed later
        db.session.add(load_data)

    # Commit the changes to the database
    db.session.commit()
    print("Data imported successfully.")

def main():
    with app.app_context():
        db.create_all()

    # function to load excel data
    file_path = os.path.abspath('load_forecast_data.xlsx')
    if os.path.exists(file_path):
        # Call import_data within the application context
        with app.app_context():
            import_data(file_path, 'Aggressive Electrification')
        print("sucessfully loaded excel data")
    else:
        print(f"File '{file_path}' not found.")

if __name__ == '__main__':
    main()
    print("Before app.run()")
    app.run(debug=True, use_reloader=False)
    print("After app.run()")

# Handles session info before requests
@app.before_request
def set_user_id():
    if 'user_id' in session:
        g.user_id = session['user_id']
    else:
        # Generate a new user_id using UUID
        g.user_id = str(uuid.uuid4())
        session['user_id'] = g.user_id

# After_request function
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

def calculator(evs_pt, pumps_pt, pvs_pt):
    #clearing data (just for testing purposes)
    db.session.query(CalculatedLoads).delete()
    db.session.commit()

    loads = Loads.query.all()

    # # Getting session id
    # session['user_id'] = session.sid

    calculated_loads_list = []

    for record in loads:
        ev_central_new = evs_pt * record.ev_central
        ev_south_new = evs_pt * record.ev_south
        ev_north_new = evs_pt * record.ev_north
        pv_central_new = pvs_pt * record.pv_central
        pv_south_new = pvs_pt * record.pv_south
        pv_north_new = pvs_pt * record.pv_north
        hp_central_new = pumps_pt * record.hp_central
        hp_south_new = pumps_pt * record.hp_south
        hp_north_new = pumps_pt * record.hp_north

        central_total_new = ev_central_new + hp_central_new + record.base_central
        south_total_new = ev_south_new + hp_south_new + record.base_south
        north_total_new = ev_north_new + hp_north_new + record.base_north

        central_total_pv_new = central_total_new + pv_central_new 
        south_total_pv_new = south_total_new + pv_south_new
        north_total_pv_new = north_total_new + pv_north_new

        no_pv_total_new = central_total_new + south_total_new + north_total_new 
        grand_total_new = central_total_pv_new + south_total_pv_new + north_total_pv_new 

        calculated_load = CalculatedLoads(
            hour=record.hour,
            base_central=record.base_central,
            base_south=record.base_south,
            base_north=record.base_north,
            ev_central=ev_central_new,
            ev_south=ev_south_new,
            ev_north=ev_north_new,
            hp_central=hp_central_new,
            hp_south=hp_south_new,
            hp_north=hp_north_new,
            pv_central=pv_central_new,
            pv_south=pv_south_new,
            pv_north=pv_north_new,
            central_total=central_total_new,
            south_total=south_total_new,
            north_total=north_total_new,
            central_total_pv=central_total_pv_new,
            south_total_pv=south_total_pv_new,
            north_total_pv=north_total_pv_new,
            no_pv_total = no_pv_total_new,
            grand_total = grand_total_new,
            user_id = g.user_id)
        
        # Add the instance to the list
        calculated_loads_list.append(calculated_load)

    db.session.add_all(calculated_loads_list)
    db.session.commit()

def summarize():
    # # Getting session id
    # session['user_id'] = session.sid

    current_id = g.user_id

    # 1) Total Annual Energy [TWh]
    total_subquery = db.session.query(
    func.coalesce(func.sum(CalculatedLoads.grand_total), 0)).filter(
        CalculatedLoads.user_id == current_id).scalar_subquery()
    # 2) Heat Pump Energy [TWh]   
    hp_subquery = db.session.query(
    func.coalesce(func.sum(CalculatedLoads.hp_central), 0) +
    func.coalesce(func.sum(CalculatedLoads.hp_south), 0) +
    func.coalesce(func.sum(CalculatedLoads.hp_north), 0)).filter(
        CalculatedLoads.user_id == current_id).scalar_subquery()
    # 3) Electrical Vehicle Energy [TWh]
    ev_subquery = db.session.query(
    func.coalesce(func.sum(CalculatedLoads.ev_central), 0) +
    func.coalesce(func.sum(CalculatedLoads.ev_south), 0) +
    func.coalesce(func.sum(CalculatedLoads.ev_north), 0)).filter(
        CalculatedLoads.user_id == current_id).scalar_subquery()
    # 4) Residential Solar Energy [TWh]
    pv_subquery = db.session.query(
    func.coalesce(func.sum(CalculatedLoads.pv_central), 0) +
    func.coalesce(func.sum(CalculatedLoads.pv_south), 0) +
    func.coalesce(func.sum(CalculatedLoads.pv_north), 0)).filter(
        CalculatedLoads.user_id == current_id).scalar_subquery()
    # 5) Peak Load Demand [MW]
    peak_load_subquery = db.session.query(
        func.max(CalculatedLoads.grand_total)
    ).filter(CalculatedLoads.user_id == current_id).scalar_subquery()
    # 6) Low Load Demand [MW] 
    low_load_subquery = db.session.query(
        func.min(CalculatedLoads.grand_total)
    ).filter(CalculatedLoads.user_id == current_id).scalar_subquery()
    # 7) Maximum Hourly Change [MW]
    hourly_change_subquery = db.session.query(
        func.abs(CalculatedLoads.grand_total - func.lag(CalculatedLoads.grand_total).over(order_by=CalculatedLoads.record_id))
    ).filter(CalculatedLoads.user_id == current_id).scalar_subquery()

    max_change_subquery = db.session.query(func.max(hourly_change_subquery)).scalar_subquery()

    query = db.session.query(
        total_subquery.label('total_value'),
        hp_subquery.label('hp_value'),
        ev_subquery.label('ev_value'),
        pv_subquery.label('pv_value'),
        peak_load_subquery.label('peak_load_value'),
        low_load_subquery.label('low_load_value'),
        hourly_change_subquery.label('hourly_change_value'),
        max_change_subquery.label('max_change_value'))

    result = query.first()

    # Executing all queries. 
    total_value, hp_value, ev_value, pv_value, peak_load_value, low_load_value, max_change_value = (
    round(result.total_value / 1000000, 2),
    round(result.hp_value / 1000000, 1), 
    round(result.ev_value / 1000000, 1),
    round(result.pv_value / 1000000, 1), 
    round(result.peak_load_value), 
    round(result.low_load_value), 
    result.max_change_value)


# 8) Number of Installed Heat Pumps, BTM, EVs.
# - multiply from capacities table
    TOTAL_EV = 448977 
    TOTAL_HP = 262832
    TOTAL_BTM = 1314

    user_info = Users.query.filter_by(user_id=g.user_id).first()

    forecast_ev = round(user_info.ev_pt * TOTAL_EV)
    forecast_hp = round(user_info.hp_pt * TOTAL_HP)
    forecast_btm = round(user_info.pv_pt * TOTAL_BTM)

    # converting back to the user's input for display purposes. 
    user_ev_pt = round(user_info.ev_pt * 90)
    user_hp_pt = round(user_info.hp_pt * 90)
    user_pv_pt = round(user_info.pv_pt * 90)

# returning all values to be included in table. 
    return (total_value, hp_value, ev_value, pv_value, peak_load_value, 
    low_load_value, max_change_value, forecast_ev, forecast_hp, forecast_btm, 
    user_ev_pt, user_hp_pt, user_pv_pt)


@app.route('/clear_data')
def clear_data():
    print("cleared data.")
    print(g.user_id)
    current_calculated_loads = CalculatedLoads.query.filter_by(user_id=g.user_id).all()
    for load in current_calculated_loads:
        db.session.delete(load)
    db.session.commit()
    session.clear()
    return "Session data cleared."

# About (displaying page about site's creators)
@app.route("/about", methods=["GET"])
def about():
        # Rendering about page
        return render_template("about.html")

# Index (home page of site)
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST": 
        evs = int(request.form.get("value1"))/(100 * .9)
        pvs = int(request.form.get("value2"))/(100 * .9)
        pumps = int(request.form.get("value2"))/(100 * .9)
        calculator(evs, pvs, pumps)
        # clearing the user table for testing purposes. 
        db.session.query(Users).delete()
        db.session.commit()

        new_user = Users(user_id = g.user_id, ev_pt=evs, pv_pt = pvs, hp_pt = pumps)
        db.session.add(new_user)
        db.session.commit()
        return redirect("/visualizations")
    else:
        # Rendering homepage if GET is used
        return render_template("index.html")
    
# visualizations for displaying graph!
@app.route("/visualizations", methods=["GET"])
def visualizations():
    return render_template('visualizations.html')
    # return render_template("visualizations.html", graph_json=graph_json)

@app.route('/get_graph_json')
def get_graph_json():
    user_id = g.user_id 

    # Fetching user's calculated loads
    data = CalculatedLoads.query.filter_by(user_id=user_id).all()

    columns_to_plot = ['ev_central', 'ev_south', 'ev_north', 'hp_central', 
                       'hp_south','hp_north', 'pv_central', 'pv_south', 'pv_north',
                       'central_total', 'south_total', 'north_total',
                       'central_total_pv', 'south_total_pv', 'north_total_pv',
                       'no_pv_total', 'grand_total']

    data_dict = {column: [getattr(record, column) for record in data] for column in columns_to_plot}
    # Create traces for each column
    traces = [go.Scatter(x=[record.hour for record in data], y=data_dict[column], mode='lines', name=column) for column in columns_to_plot]
    # Create the layout and figure
    # layout = go.Layout(title='Hourly Load Categories Over Time', xaxis=dict(title='Month'), yaxis=dict(title='Load (MW)'))
    layout = go.Layout(
        title=go.layout.Title(
            text='<b>Hourly Load Categories Over Time<b>',
            font=dict(family='Times New Roman, serif', size=24,),
            xref='paper'),
        xaxis=dict(
            title='Month', 
            titlefont=dict(family='Times New Roman,serif', size=14,)), 
        yaxis=dict(
            title='Load (MW)', 
            titlefont=dict(family='Times New Roman,serif', size=14,)),)
        
    fig = go.Figure(data=traces, layout=layout)

    # Convert the figure to JSON using Plotly's built-in function
    graph_json = fig.to_json()

    return jsonify(graph_json)
    
# summarized data format
@app.route("/data", methods=["GET", "POST"])
def data():
    if request.method == "POST": 
         print("post")
    else:
        (total_value, hp_value, ev_value, pv_value, peak_load_value, 
        low_load_value, max_change_value, forecast_ev, forecast_hp, 
        forecast_btm, user_ev_pt, user_hp_pt, user_pv_pt) = summarize()
        # Rendering homepage if GET is used
        return render_template("data.html", total_value=total_value, 
            hp_value=hp_value, ev_value=ev_value, pv_value=pv_value,
            peak_load_value=peak_load_value, low_load_value=low_load_value, 
            max_change_value=max_change_value, forecast_ev=forecast_ev, 
            forecast_hp=forecast_hp, forecast_btm=forecast_btm, 
            user_ev_pt=user_ev_pt, user_hp_pt=user_hp_pt, user_pv_pt=user_pv_pt)
    

