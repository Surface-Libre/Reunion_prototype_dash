"""
This script creates a Dash application with a navbar and a callback function 
for toggling the navbar collapse.
"""

from dash import html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import dash

# Navbar component
navbar = dbc.Navbar(
    dbc.Container(
        [
            dbc.Row([
                dbc.Col([
                    html.Img(src=dash.get_asset_url('logo.png'), height="40px"),
                    dbc.NavbarBrand("Prototype Real-Time RUENION App", className="ms-2")
                ],
                width={"size": "auto"})
            ],
            align="center",
            className="g-0"),

            dbc.Row([
                dbc.Col([
                    dbc.Nav([
                        dbc.NavItem(dbc.NavLink("Interface Graphique", href="/")),
                        dbc.NavItem(dbc.NavLink("Cartographie Lizmap", href="/lizmap")),
                        dbc.NavItem(dbc.NavLink("Simulation Run", href="/simrun"))
                    ],
                    navbar=True
                    )
                ],
                width={"size": "auto"})
            ],
            align="right"),
            dbc.Col(dbc.NavbarToggler(id="navbar-toggler", n_clicks=0)),

        ],
        fluid=True
    ),
    color="primary",
    dark=True
)


@dash.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    """
    Callback function to toggle the navbar collapse state.

    Args:
        n (int): Number of times the navbar toggler has been clicked.
        is_open (bool): Current state of the navbar collapse.

    Returns:
        bool: Updated state of the navbar collapse.
    """
    if n:
        return not is_open
    return is_open

