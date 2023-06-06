"""
This script defines the layout for the Lizmap app page in the Dash application.
"""
import dash
from dash import dcc, html


from apps import navigationbar

dash.register_page(__name__, path='/lizmap', title="Interface graphic",
                   description="Interface graphic", image='logo.png')

layout = html.Div([
    navigationbar.navbar,
    dcc.Interval(id="iframe-interval", interval=1000, disabled=True),
    html.Iframe(
        id='lizmap',
        src="https://carto.surfacelibre.fr/admin.php/auth/login/?auth_url_return=%2Findex.php%2Fview%2F",
        width="100%",
        height="100%"
    ),
], style={'height': '100%', 'width': '100%', "position": "absolute"})
