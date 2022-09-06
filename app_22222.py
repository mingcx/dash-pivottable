from flask import Flask, url_for, send_file, send_from_directory
from flask import render_template
from markupsafe import escape
from flask import request
import pandas as pd
from datetime import datetime
import urllib
from dash import Dash, dcc, html, Input, Output, State
import json
import plotly
import plotly.express as px

server = Flask(__name__)

@server.route("/")
def home():
    return "Hello, Flask!"

@server.route("/dash")
def dash111():
    app= Dash(server=server, routes_pathname_prefix="/dash/")



    # assume you have a "long-form" data frame
    # see https://plotly.com/python/px-arguments/ for more options
    df1 = pd.DataFrame({
        "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
        "Amount": [4, 1, 2, 2, 4, 5],
        "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
    })

    fig = px.bar(df1, x="Fruit", y="Amount", color="City", barmode="group")

    app.layout = html.Div(children=[
        html.H1(children='Hello Dash'),

        html.Div(children='''
            Dash: A web application framework for your data.
        '''),

        dcc.Graph(
            id='example-graph',
            figure=fig
        )
    ])          


if __name__ == "__main__":
    app.run_server(debug=True)