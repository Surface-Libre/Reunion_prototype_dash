"""
This script defines the layout for the graphic interface app page in the Dash application.
"""

import os
import sys
import glob
import time

import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import dash_datetimepicker
import dash_leaflet as dl
import pandas as pd
import numpy as np

from pydsstools.heclib.dss import HecDss

from apps import navigationbar

from pages.mapping_element.map import add_shapfile_stations, add_shapfile_bv, add_shapfile_riv

sys.path.append(os.getcwd()+'\\src\\pages\\')

dash.register_page(__name__, path='/', title="Prototype Réunion",
                   description="Prototype_Réunion", image='logo.png')

dss_file = glob.glob(os.getcwd() + '/src/data/*/*.dss', recursive=True)[0]
dss_file_hist = "C:\\Users\\33751\\Downloads\\Modele_Hydrologie_Dashboard\\Modele_Hydrologie_Dashboard\\HydroSJ_Obs.dss"

station_cd = {'4030000301': 'PteStJeanDelices', '4030000101': 'GdeStJeanRn2002',
              '4030000201': 'GdeStJeanGdBras', '4030000901': 'GdeStJeanPichon'}

tile = dl.TileLayer()
stations = add_shapfile_stations()
river = add_shapfile_riv()
bv = add_shapfile_bv()


def get_timeseries(station, start_date=False, end_date=False):
    """
    Get timeseries data for a given station and date range.

    Args:
        station (str): Station code.
        startDate (datetime, optional): Start date of the date range. Defaults to False.
        endDate (datetime, optional): End date of the date range. Defaults to False.

    Returns:
        tuple: Two arrays representing the times and values of the timeseries data.
    """
    if station is None:
        return None, None

    pathname = "/REFERENCE LINES/2D: " + station + "/FlOW//1Minute/FAK_S5/"
    window = (start_date, end_date) if start_date and end_date else None
    ts = HecDss.Open(dss_file).read_ts(
        pathname, window=window, trim_missing=True)

    times = np.array(ts.pytimes)
    values = np.round(ts.values, 2)

    return times, values


def get_timeseries_obs(station, start_date=False, end_date=False):
    """
    Get observed timeseries data for a given station and date range.

    Args:
        station (str): Station code.
        startDate (datetime, optional): Start date of the date range. Defaults to False.
        endDate (datetime, optional): End date of the date range. Defaults to False.

    Returns:
        tuple: Two arrays representing the times and values of the observed timeseries data.
    """
    if station in station_cd:
        pathname = "/RL_OBS/" + \
            station_cd[station] + "/FLOW//IR-Decade/Reunion/"
        window = (start_date, end_date) if start_date and end_date else None
        ts = HecDss.Open(dss_file_hist).read_ts(
            pathname, window=window, trim_missing=True)

        times = np.array(ts.pytimes)
        values = np.round(ts.values, 2)

        return times, values
    else:
        return None, None


map_layout = html.Div([
    dl.Map(
        center=[-21.10, 55.46],
        zoom=12,
        id="map",
        children=[
            dl.LayersControl([
                dl.BaseLayer(tile, name='OpenStreetMap', checked=True),
                dl.Overlay(
                    stations[0], name='Stations Hydrométrqiues', checked=True),
                dl.Overlay(
                    river[0], name='Réseau Hydrographique', checked=True),
                dl.Overlay(bv[0], name='Bassins Versants', checked=True)
            ])
        ],
        style={"height": "100%", "width": "100%",
               "position": "absolute", "z-index": "0"}
    )
], style={"height": "100%", "width": "100%", "position": "absolute", "z-index": "0"})

control = [
    dbc.CardHeader("Pannel de contôle de visualisation"),
    dbc.CardBody(
        [
            dbc.Label("Choisissez la station hydrométique:",
                      style={'font-weight': 'bold'}),
            dcc.Dropdown(
                id="station-dropdown",
                options=[{"label": s, "value": s}
                         for s in stations[1]["Name"]],
                value=[stations[1]["Name"][0]],
                persistence=True,
                persistence_type='local'
            ),
            dbc.Label("Choisissez la date et l'heure:",
                      style={'font-weight': 'bold'}),
            dash_datetimepicker.DashDatetimepicker(
                id='datetime-picker-range'
            ),
            dbc.Label("Télécharger Data Simulation .CSV",
                      style={'font-weight': 'bold'}),
            dcc.Download(id="download-data-csv"),
            html.Button("Download CSV", id="btn-download"),

        ]
    )
]

graph = [
    dbc.CardHeader("Visualisation des débits"),
    dbc.CardBody(
        [
            html.Div(id="graph",
                     style={"width": "100%", "height": "100%","position":"absolute"})
        ]
    ),
]

layout = [
    navigationbar.navbar,
    map_layout,
    html.Br(),
    dbc.Card(control, color="secondary", outline=True,
             style={"width": "25%", "top": "10%", "position": "absolute"}),
    html.Br(),
    dbc.Card(graph, color="secondary", outline=True,
             style={"width": "50%", "height": "60%", "top": "30%", "position": "absolute"}),
    dcc.Store(id='ts-data-store-sim', storage_type='local'),
    dcc.Store(id='ts-data-store-obs', storage_type='local'),
]


@dash.callback(
    [
        Output('datetime-picker-range', 'startDate'),
        Output('datetime-picker-range', 'endDate'),
        Output('ts-data-store-sim', 'data'),
        Output('ts-data-store-obs', 'data')
    ],
    [Input('station-dropdown', 'value')],
    prevent_initial_call=True
)
def update_datetime_picker_range(selected_station):
    """
    Callback function to update the datetime picker range and data stores 
    based on the selected station.

    Args:
        selected_station (str): The selected station value from the dropdown.

    Returns:
        tuple: Start date, end date, simulated data, observed data.
    """
    times_sim, values_sim = get_timeseries(selected_station)
    times_obs, values_obs = get_timeseries_obs(selected_station)

    if times_sim is None or len(times_sim) == 0:
        start_date = None
        end_date = None
    else:
        start_date = str(times_sim[0])
        end_date = str(times_sim[-1])

    data_sim = {'time': times_sim, 'value': values_sim}
    data_obs = {'time': times_obs, 'value': values_obs}

    return start_date, end_date, data_sim, data_obs

@dash.callback(
    [Output("download-data-csv", "data")
    ],
    [
    Input("btn-download", "n_clicks"),
    Input('ts-data-store-sim', 'data'),
    Input('station-dropdown', 'value')],
    prevent_initial_call=True
)
def download_data_csv(n_clicks,data_sim,selected_station):

    df_sim = pd.DataFrame({'Time': data_sim['time'], 'value de débit (m3/s)': data_sim['value']})
    print(type(df_sim))
    return dcc.send_data_frame(df_sim.to_csv, f"{selected_station}.csv")
 
    
    
@dash.callback(
    Output('graph', 'children'),
    [
        Input('station-dropdown', 'value'),
        Input('datetime-picker-range', 'startDate'),
        Input('datetime-picker-range', 'endDate'),
    ],
    [
        State('ts-data-store-sim', 'data'),
        State('ts-data-store-obs', 'data')
    ],
    prevent_initial_call=True
)
def update_chart(selected_station, start_date, end_date, data_sim, data_obs):
    """
    Callback function to update the chart based on the selected station, date range, and data.

    Args:
        selected_station (str): The selected station value from the dropdown.
        startDate (str): The start date of the date range.
        endDate (str): The end date of the date range.
        data_sim (dict): Simulated data.
        data_obs (dict): Observed data.

    Returns:
        dcc.Graph: The updated timeseries chart.
    """
    # Filter the timeseries data by the selected station, date range, and parameter
    start_time = time.time()
    print(f'the value of selected is {selected_station}')
    print(f'the value of selected is {start_date}')
    print(f'the value of selected is {end_date}')
    print(selected_station)
    
    # Get the results
    times_obs, values_obs = data_obs['time'], data_obs['value']
    times_sim, values_sim = data_sim['time'], data_sim['value']

    # Use Plotly Express to create the chart
    fig = go.Figure()

    if times_obs is not None and values_obs is not None:
        # Add observed flow trace
         fig.add_trace(go.Scatter(x=times_obs, y=values_obs,
                        name="Observed Flow", line=dict(color='green')))

    # Add simulated flow trace
    fig.add_trace(go.Scatter(x=times_sim, y=values_sim,
                    name="Simulated Flow", line=dict(color='red')))
        
        
    fig.add_vline(x=times_sim[-1], line_width=3,
                        line_dash="dash", line_color="blue") 
            
        # Set up the layout of the chart
    fig.update_layout(
                height=600,
                width=1000,
                title=f'Station {station_cd[selected_station] if selected_station in station_cd else selected_station } // max_values= {str(np.amax(values_sim))} // Tmax={str(times_sim[np.argmax(values_sim)])}',
                xaxis=dict(title='Date', zeroline=True,
                        zerolinecolor='gray', ticks='outside'),
                yaxis=dict(title='Flow [m^3/s]', zeroline=True,
                        zerolinecolor='gray', ticks='outside', fixedrange=True),
                showlegend=True,  # Show the legend
                legend=dict(orientation="h", yanchor="bottom", y=1.02,
                            xanchor="right", x=1),  # Legend position
        )
            
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Callback execution time: {execution_time} seconds")

    return dcc.Graph(id="timeseries-chart", figure=fig)


@dash.callback(
    Output("popup_stations", "children"), 
    [Input("geojson", "click_feature")],
    prevent_initial_call=True
)
def update_tooltip_stations(feature):
    """
    Callback function to update the tooltip for stations based on the clicked feature.

    Args:
        feature (dict): The clicked feature from the geojson.

    Returns:
        list: List of HTML paragraphs representing the tooltip content.
    """
    properties = {}

    if feature is not None:
        # Get the properties of the clicked feature
        properties = feature["properties"]

    return [
        html.P(f"{key}: {value}") for key, value in properties.items()
    ]


@dash.callback(Output("popup_bv", "children"), [Input("bv", "click_feature")],prevent_initial_call=True)
def update_tooltip_bv(feature):
    """
    Callback function to update the tooltip for basins based on the clicked feature.

    Args:
        feature (dict): The clicked feature from the geojson.

    Returns:
        list: List of HTML paragraphs representing the tooltip content.
    """
    properties = {}

    if feature is not None:
        # Get the properties of the clicked feature
        properties = feature["properties"]

    return [
        html.P(f"{key}: {value}") for key, value in properties.items()
    ]


@dash.callback(Output("station-dropdown", "value"), [Input("geojson", "click_feature")],prevent_initial_call=True)
def update_value_dropdown(feature):
    """
    Callback function to update the value of the station dropdown based on the clicked feature.

    Args:
        feature (dict): The clicked feature from the geojson.

    Returns:
        str: The updated value of the station dropdown.
    """
    value = None
    if feature is not None:
        value = feature['properties']['Name']
    return value

