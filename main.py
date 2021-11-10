import pandas as pd

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input
import plotly.graph_objects as go


def filterData() -> pd.DataFrame:

    df = pd.read_csv("https://data.rivm.nl/covid-19/COVID-19_aantallen_gemeente_per_dag.csv", sep=';')
    df['cumulative'] = df.groupby(['Municipality_name'])['Total_reported'].cumsum()

    columns = ['Date_of_publication','Municipality_name', 'Total_reported', 'cumulative']

    return df[columns]

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
            style={"flex-grow": "1", "display": "inline-block"})
        ], style={"display": "flex", "height": "100vh"})

    return layout

DATA = filterData()
DEFAULT_CITIES = ['Amsterdam', 'Rotterdam', 'Eindhoven','Tilburg']

# Get sorted list of cities in the data
cities = DATA['Municipality_name'].dropna().unique()
cities.sort()

stylesheet = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=stylesheet)

app.layout = createLayout(cities, DEFAULT_CITIES)
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

    number_data = kind_map[kind]
    grouped_data = DATA.groupby('Municipality_name')

    ylabel = y_axes[kind]
    layout = go.Layout(
        title='Covid Infections in the Netherlands',
        xaxis=dict(
            title='Date',
            showgrid=False),
        yaxis=dict(
            title=ylabel,
            showgrid=False),
        hovermode='x unified',
        template='plotly_dark',
        paper_bgcolor='#121212',
        plot_bgcolor='#121212')
    
    fig = go.Figure(layout=layout)

    for city in cities:

        city_data = grouped_data.get_group(city)
        x = city_data['Date_of_publication']
        y = city_data[number_data]

        scatter = go.Scatter(x=x, y=y, name=city)
        fig.add_trace(scatter)

    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
