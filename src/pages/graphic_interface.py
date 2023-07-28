"""
This script defines the layout for the graphic interface app page in the Dash application.
"""

import os
import sys
import time


import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

import plotly.graph_objects as go
from plotly.subplots import make_subplots

import dash_datetimepicker
import dash_leaflet as dl
import pandas as pd
import numpy as np
from datetime import datetime


from pydsstools.heclib.dss import HecDss

from apps import navigationbar
from apps import config_to_dash


from pages.mapping_element.map import add_shapfile_stations, add_shapfile_bv, add_shapfile_riv

sys.path.append(os.getcwd()+'\\src\\pages\\')

dash.register_page(__name__, path='/', title="Prototype Réunion",
                   description="Prototype_Réunion", image='logo.png')

dss_file = r"{}".format(config_to_dash.dss_file_simulation)
dss_file_hist = r"{}".format(config_to_dash.dss_file_observation_data)
dss_bv_rainfall=r"{}".format(config_to_dash.dss_file_rainfall_bv)

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
    

def get_timeseries_rainfall(station, start_date=False, end_date=False):
    """
    Get observed timeseries data for a given station and date range.

    Args:
        station (str): Station code.
        startDate (datetime, optional): Start date of the date range. Defaults to False.
        endDate (datetime, optional): End date of the date range. Defaults to False.

    Returns:
        tuple: Two arrays representing the times and values of the observed timeseries data.
    """
    pathname = "/A/" + \
            station + "/A//15Minute/antilope/"
    window = (start_date, end_date) if start_date and end_date else None
    ts = HecDss.Open(dss_bv_rainfall).read_ts(
            pathname, window=window, trim_missing=True)

    times = np.array(ts.pytimes)
    values_15min = np.round(ts.values, 2)
        
    data = pd.DataFrame({
         'Times': times, 'Values_15min': values_15min})
        
    for i in range(2, 25):
        data['CUM_' + str(i)] = data['Values_15min'].rolling(i).sum()

        # Calculate the cumulative sum of hourly data
    values_1h = np.array(np.round(data['CUM_4'].values,2))
        
        
        
        # Calculate the cumulative sum of 3-hourly data
    values_3h = np.array(np.round(data['CUM_12'].values,2))
        
        
        # Calculate the cumulative sum of 6-hourly data
    values_6h = np.array(np.round(data['CUM_24'].values,2))
        
        
    
    return times, values_15min,values_1h,values_3h,values_6h



def plots(data_sim,data_obs, data_rainfall_prv,timestep,selected_station,start_date,end_date):
    """
    Plots the simulated and observed debits and rainfall data for a given station and time range.

    Parameters:
    -----------
    data_sim : dict
        A dictionary containing the simulated debits data with keys 'time' and 'debits(m3/s)'.
    data_obs : dict
        A dictionary containing the observed debits data with keys 'time' and 'debits(m3/s)'.
    data_rainfall_prv : dict
        A dictionary containing the rainfall data with keys 'time', 'pluie_1h(mm)', 'pluie_3h(mm)', and 'pluie_6h(mm)'.
    timestep : str
        The timestep of the rainfall data to plot, e.g., 'pluie_1h(mm)', 'pluie_3h(mm)', or 'pluie_6h(mm)'.
    selected_station : str
        The code of the selected station.
    start_date : str
        The start date of the desired range in the format 'YYYY-MM-DD'.
    end_date : str
        The end date of the desired range in the format 'YYYY-MM-DD'.

    Returns:
    --------
    fig : plotly.graph_objs._figure.Figure
        A Plotly figure object containing the plotted data.
    """

    if data_obs['time'] is not None:
        times_obs, values_obs= np.array([np.datetime64(d) for d in data_obs['time']]), np.array(data_obs['debits(m3/s)'])
    else:
        
        times_obs, values_obs=None, None
    times_sim, values_sim =np.array([np.datetime64(d) for d in data_sim['time']]), np.array(data_sim['debits(m3/s)'])
    times_rainfall, values= np.array([np.datetime64(d) for d in data_rainfall_prv['time']]), np.array(data_rainfall_prv[timestep])

    values_1h=np.array(data_rainfall_prv["pluie_1h(mm)"])
    values_3h=np.array(data_rainfall_prv["pluie_3h(mm)"])
    values_6h=np.array(data_rainfall_prv["pluie_6h(mm)"])

    

    # Define the start and end dates for the desired range
    start_date = np.datetime64(start_date)
    end_date = np.datetime64(end_date)


    if times_rainfall.size>1 and values.size>1 and values_1h.size>1 and values_3h.size>1 and values_6h.size>1:
        values[np.where(values == None)] = np.nan
        values_1h[np.where(values_1h == None)] = np.nan
        values_3h[np.where(values_3h == None)] = np.nan
        values_6h[np.where(values_6h == None)] = np.nan
        
    else:
        pass

    max15min=np.round(np.nanmax(values),0)
    max1H=np.round(np.nanmax(values_1h),0)
    max3H=np.round(np.nanmax(values_3h),0)
    max6H=np.round(np.nanmax(values_6h),0)
    

    # Create the subplots
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0, row_heights=[0.4, 0.8])

    # Add the second subplot
    fig.add_trace(go.Scatter(
        x=times_sim,
        y=values_sim,
        name='Débits Simulés',
        mode='lines',
        line_color='red',
        line_width=1.5,
        hovertemplate='Débit: %{y} (m3/s), t:%{x}',
    ), row=2, col=1)

    fig.add_trace(go.Scatter(
        x=times_obs, 
        y=values_obs, 
        name="Débits Observés",
        mode='lines',
        line_color='green',
        line_width=1.5,
        hovertemplate='Débit: %{y} (m3/s), t:%{x}',
    ), row=2, col=1)

    fig.add_trace(go.Bar(
        x=times_rainfall, 
        y=values,  
        width=2,
        name="Pluie de bassins(ou pluies cumulées)",
        marker_opacity=0.9,
        marker_line_color='blue',
        marker_line_width=5,
        hovertemplate='Pluie: %{y} (mm/pas_de_temps)',
    ), row=1, col=1)
    

    fig.update_xaxes(range=[start_date,end_date ], row=2, col=1)
    fig.update_xaxes(gridcolor='lightgray', gridwidth=1, row=2, col=1)

    # Update the layout
    fig.update_layout(
        height=800,

        title=f'Station {station_cd[selected_station] if selected_station in station_cd else selected_station } // max_values= {str(np.round(np.amax(values_sim),2))} // Tmax={str(times_sim[np.argmax(values_sim)])}',
        title_font_family='Courier New',
        title_font_size=18,
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(
            title_font=dict(size=12),
            tickangle=90,
            tickfont=dict(size=12),
            tickmode='array',
            showgrid=True,
            gridcolor='lightgray',
            zeroline=True,
            linewidth=1,
            linecolor='black',
            tickwidth=2,
            tickcolor='black',
            side='bottom',
            ticks="inside",
        ),
        yaxis=dict(
            title='Pluie (mm/15 min)',
            title_font=dict(size=16),
            tickfont=dict(size=16),
            ticks="inside",
            zeroline=True,
            zerolinecolor='gray',
            zerolinewidth=1,
            showline=True,
            linewidth=1,
            linecolor='black',
            autorange='reversed'
        ),
        yaxis2=dict(
            title='Débit (m3/s)',
            title_font=dict(size=16),
            tickfont=dict(size=16),
            ticks="inside",
            zeroline=True,
            zerolinecolor='gray',
            zerolinewidth=1,
            showline=True,
            linewidth=1,
            linecolor='black'
        ),
        margin=dict(l=20, r=0, t=50, b=50),
        showlegend=True,
        shapes=[
            # Rectangle frame
            dict(
                type="rect",
                xref="paper",
                yref="paper",
                x0=0,
                y0=0,
                x1=1,
                y1=1,
                line=dict(
                    color="black",
                    width=1,
                    dash="solid",
                ),
            )
        ]
    )

    fig.add_annotation(
        xref="x domain",
        yref="y domain",
        x=0.97,
        y=0.1,
        text=f'Cumul Max_15Min =' + str(max15min)+'mm'+'<br>' +
         'Cumul Max_1h =' + str(max1H) +'mm'+ '<br>' +
         'Cumul Max_3h =' + str(max3H) +'mm'+ '<br>' +
         'Cumul Max_6h =' + str(max6H)+'mm',
        showarrow=False,
        font=dict(
            family='Courier New',
            size=18,
            color='black'
        )
    )

    fig.update_layout(
        title_font_family='Courier New',
        title_font_size=18,
        xaxis_title_font_family='Courier New',
        xaxis_title_font_size=16,
        yaxis_title_font_family='Courier New',
        yaxis_title_font_size=16,
        yaxis2_title_font_family='Courier New',
        yaxis2_title_font_size=16
    )
    fig.update_layout(
        legend_font_color='black',
        legend_font_size=12
    )
    
    
    return fig

map_layout = html.Div([
    dl.Map(
        center=[-21.10, 55.46],
        zoom=15,
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
            html.Br(),
            html.Button("Download CSV", id="btn_csv",className="btn btn-primary"),
            dcc.Download(id="download-dataframe-csv"),
            

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
             style={"width": "52%", "height": "60%", "top": "30%", "position": "absolute"}),
    dcc.Store(id='ts-data-store-sim', storage_type='local'),
    dcc.Store(id='ts-data-store-obs', storage_type='local'),
    dcc.Store(id='ts-data-store-rf-bv', storage_type='local'),
]


@dash.callback(
    [
        Output('datetime-picker-range', 'startDate'),
        Output('datetime-picker-range', 'endDate'),
        Output('ts-data-store-sim', 'data'),
        Output('ts-data-store-obs', 'data'),
        Output('ts-data-store-rf-bv','data')
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
        tuple: Start date, end date, simulated data, observed data, rainfall values of subbassins
    """
    times_sim, values_sim = get_timeseries(selected_station)
    times_obs, values_obs = get_timeseries_obs(selected_station)
    times_rainfall, values_15min,values_1h,values_3h,values_6h=get_timeseries_rainfall(selected_station)

    if times_sim is None or len(times_sim) == 0:
        start_date = None
        end_date = None
    else:
        start_date = str(times_sim[0])
        end_date = str(times_sim[-1])

    data_sim = {'time': times_sim, 'debits(m3/s)': values_sim}
    data_obs = {'time': times_obs, 'debits(m3/s)': values_obs}
    data_pbv={'time': times_rainfall, 'pluie_15min(mm)': values_15min, 'pluie_1h(mm)': values_1h,'pluie_3h(mm)': values_3h,'pluie_6h(mm)': values_6h}

    return start_date, end_date, data_sim, data_obs, data_pbv


@dash.callback(
    [Output("download-dataframe-csv", "data")
    ],
    [
    Input("btn_csv", "n_clicks"),
    Input('ts-data-store-sim', 'data'),
    Input('station-dropdown', 'value')],
    prevent_initial_call=True
)
def download_data_csv(n_clicks,data_sim,selected_station):
    """
    callbacks to download csv data
    
    """
    ctx = dash.callback_context

    if ctx.triggered[0]['prop_id'].split('.')[0] != 'btn_csv' or n_clicks is None:
        return [None]

    else:
        df_sim = pd.DataFrame({'Time': data_sim['time'], 'débits (m3/s)': data_sim['debits(m3/s)']})

        return [dcc.send_data_frame(df_sim.to_csv, filename=f"ts_{selected_station}.csv")]

@dash.callback(
    Output('graph', 'children'),
    [
        Input('station-dropdown', 'value'),
        Input('datetime-picker-range', 'startDate'),
        Input('datetime-picker-range', 'endDate'),
    ],
    [
        State('ts-data-store-sim', 'data'),
        State('ts-data-store-obs', 'data'),
        State('ts-data-store-rf-bv','data')
    ],
    prevent_initial_call=True
)
def update_chart(selected_station, start_date, end_date, data_sim, data_obs,data_rainfall_prv):
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

    start_date=start_date.replace(' ', 'T')
    end_date=end_date.replace(' ', 'T')

    fig = plots(data_sim, data_obs, data_rainfall_prv, "pluie_15min(mm)", selected_station,start_date,end_date)

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


