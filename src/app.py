"""
This script initializes the Dash application of Protoype Réunion and runs the server.
"""

import os
import glob

import dash
import dash_bootstrap_components as dbc
from dash import html


assets_folder_path = os.path.join(os.getcwd(), 'src', 'assets')

app = dash.Dash(__name__,
                suppress_callback_exceptions=True,
                prevent_initial_callbacks=True,
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}],
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                use_pages=True)
server = app.server

app.layout = html.Div(children=[
    dash.page_container
], style={'padding': '0', "position": "absolute", "height": "100%", "width": "100%",
        "z-index": "0"})

if __name__ == "__main__":
    # app.run_server(debug=True)
    app.run_server(debug=False, port=5050)



