from dash_html_components.Label import Label
import pandas as pd
import numpy as np

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input
import plotly.graph_objects as go


def filter_data() -> pd.DataFrame:

    df = pd.read_csv("https://data.rivm.nl/covid-19/COVID-19_aantallen_gemeente_per_dag.csv", sep=';')
    df['cumulative'] = df.groupby(['Municipality_name'])['Total_reported'].cumsum()

    columns = ['Date_of_publication','Municipality_name', 'Total_reported', 'cumulative']

    return df[columns]

def draw_graph(data, cities, kind='CUM'):

    kind_map = {
        "CUM": "cumulative",
        "PD": "Total_reported"
    }

    number_data = kind_map[kind]
    grouped_data = data.groupby('Municipality_name')
    fig = go.Figure()

    for city in cities:

        city_data = grouped_data.get_group(city)
        x = city_data['Date_of_publication']
        y = city_data[number_data]

        scatter = go.Scatter(x=x, y=y, name=city)
        fig.add_trace(scatter)
    
    y_axes = {
        "CUM": "Number of cases",
        "PD": "Number of cases per day" 
    }
    ylabel = y_axes[kind]

    fig.update_layout(title='Test', hovermode='x unified')
    fig.update_xaxes(title="Date")
    fig.update_yaxes(title=ylabel)

    return fig

def create_layout(cities, default_cities) -> html.Div:

    city_dropdown = dcc.Dropdown(
        id='city-dropdown',
        options=[{'label': i, 'value': i} for i in cities],
        multi=True,
        value=default_cities,
        placeholder="Select cities")

    layout = html.Div(children=[

        html.Div(children=[
            html.Label(["Select cities to be plotted", city_dropdown]),
            
            html.Label(["Type of Graph", dcc.RadioItems(
                id='graph-type',
                options=[
                    {'label': 'Cumulative', "value": "CUM"},
                    {'label': "Infections Per Day", "value": "PD"}
                ], value='CUM')
                ], style={"margin": "20"})
        ], style={"display": "inline-block", "vertical-align": "top", "width": "20%"}),

        html.Div(children=[
            dcc.Graph(id='test_graph', figure=go.Figure(),
                style={"height": "100%"})], 
            style={"flex-grow": "1", "display": "inline-block"})
    ], className='row', style={"display": "flex", "height": "100vh"})

    return layout

data = filter_data()
default_cities = ['Amsterdam', 'Rotterdam', 'Eindhoven','Tilburg']

stylesheet = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=stylesheet)

# Get sorted list of cities in the data
cities = data['Municipality_name'].dropna().unique()
cities.sort()

app.layout = create_layout(cities, default_cities)

@app.callback(
    Output('test_graph', 'figure'),
    [Input('city-dropdown', 'value'),
    Input('graph-type', 'value')])
def update_graph(cities, kind):

    return draw_graph(data, cities, kind)

if __name__ == "__main__":
    app.run_server(debug=True)

