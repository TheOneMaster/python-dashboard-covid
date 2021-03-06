import time

from dash_core_components import Interval
import pandas as pd

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go

import flask

DEFAULT_CITIES = ['Amsterdam', 'Rotterdam', 'Eindhoven','Tilburg']

# Interval to update data with (Every 12 hours)
INTERVAL_TIME = 1000 * 60 * 60 * 12

START_TIME = time.time()

def getData() -> pd.DataFrame:

    df = pd.read_csv("https://data.rivm.nl/covid-19/COVID-19_aantallen_gemeente_per_dag.csv", sep=';')
    df['cumulative'] = df.groupby(['Municipality_name'])['Total_reported'].cumsum()

    df = df.groupby(['Municipality_name', 'Date_of_publication'], as_index=False).agg({
        'Total_reported': 'sum',
        'cumulative': 'last'
    })

    return df

def createLayout(cities, default_cities) -> html.Div:

    city_dropdown = dcc.Dropdown(
        id='city-dropdown',
        options=[{'label': i, 'value': i} for i in cities],
        multi=True,
        value=default_cities,
        placeholder="Select cities",
        style={
            "background-color": "var(--background-color)",
        })

    chart_type = dcc.RadioItems(
        id='graph-type',
        options=[
            {'label': 'Cumulative', "value": "CUM"},
            {'label': "Infections Per Day", "value": "PD"}
        ], value='CUM')
    
    layout = html.Div(children=[

        # Options (Left Side)
        html.Div(children=[
            html.Label(["Select cities to be plotted", city_dropdown]),
            html.Label(["Type of Graph", chart_type], style={"margin-top": "1em"})
            ], style={"display": "inline-block", "vertical-align": "top", "width": "20%", "background-color": "#121212"}),

        # Chart (Right Side)
        html.Div(children=[
            dcc.Graph(id='test_graph', figure=go.Figure(layout=dict(template='plotly_dark')),
                style={"height": "100%"})], 
            style={"flex-grow": "1", "display": "inline-block"}),
        
        # Interval
        dcc.Interval(id="data-update", interval=INTERVAL_TIME, n_intervals=0),
        html.Div(id="data-storage", children=[], style={"display": "none"})

        ], style={"display": "flex", "height": "100vh"})

    return layout

DATA = getData()
# Get sorted list of cities in the data
CITIES = DATA['Municipality_name'].dropna().unique()
CITIES.sort()

stylesheet = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

server = flask.Flask(__name__)


app = dash.Dash(
    __name__, external_stylesheets=stylesheet,
    server=server, url_base_pathname="/dash/")

app.layout = createLayout(CITIES, DEFAULT_CITIES)
app.title = "COVID Dashboard - Netherlands"

# Callbacks
@app.callback(
    Output('test_graph', 'figure'),
    [Input('city-dropdown', 'value'),
    Input('graph-type', 'value')])
def updateGraph(cities, kind) -> go.Figure:

    kind_map = {
        "CUM": "cumulative",
        "PD": "Total_reported"
    }

    y_axes = {
        "CUM": "Number of cases",
        "PD": "Number of cases per day" 
    }

    selector_options = {
        'buttons': [
            dict(count=1, label='1M', step='month', stepmode='backward'),
            dict(count=6, label='6M', step='month', stepmode='backward'),
            dict(count=1, label='1Y', step='year', stepmode='backward'),
            dict(label='All', step='all')],
        'bgcolor': "hsl(0, 0%, 20%)"
    }


    number_data = kind_map[kind]
    grouped_data = DATA.groupby('Municipality_name')

    ylabel = y_axes[kind]
    layout = go.Layout(
        title='Covid Infections in the Netherlands',
        xaxis=dict(title='Date', rangeselector=selector_options),
        yaxis=dict(title=ylabel),
        hovermode='x unified',
        template='plotly_dark',
        paper_bgcolor='#121212',
        plot_bgcolor='#121212')
    
    fig = go.Figure(layout=layout)

    fig.update_xaxes(showline=True, showgrid=False)
    fig.update_yaxes(showline=True, showgrid=True, rangemode='tozero', gridcolor='hsl(0, 0%, 40%)')

    for city in cities:

        city_data = grouped_data.get_group(city)
        x = city_data['Date_of_publication']
        y = city_data[number_data]

        scatter = go.Scatter(x=x, y=y, name=city)
        fig.add_trace(scatter)

    return fig

@app.callback(
    Output('data-storage', 'children'),
    Input('data-update', 'n_intervals'))
def updateData(n_intervals):

    global DATA

    if n_intervals is None:
        raise PreventUpdate

    start = time.time()
    DATA = getData()
    
    end = time.time()

    return [f"Data update time: {end-start:.3f}s"]


@server.route("/dash")
def my_dash_app():
    return app.index()
