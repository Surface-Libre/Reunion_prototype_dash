'''
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from flask import Flask,render_template
import dash


from app import app
from app import server


from pages import graphic_interface, mapping_lizmap, simualtion_run



tab_selected_style = {
    'width':'60%',
    'margin': '5px 0',
    'text-align':'center',
    'color':'#046474',
    'font-weight':'600',
    'cursor':'pointer',
    'font-size':'20px',
    'text-transform': 'uppercase',
    'border-radius': '10px 10px 10px 10px',
    'border': '5px solid #046474',
    'outline':'none'
}

navbar = dbc.Navbar(
            dbc.Container(
                [
                    dbc.Row([
                        dbc.Col([
                            html.Img(src=dash.get_asset_url('logo.png'), height="40px"),
                            dbc.NavbarBrand("Prototype RUENION App", className="ms-2")
                        ],
                        width={"size":"auto"})
                    ],
                    align="center",
                    className="g-0"),

                    dbc.Row([
                        dbc.Col([
                            dbc.Nav([
                                dbc.NavItem(dbc.NavLink("Interface Graphique", href="/graphic")),
                               
                                dbc.NavItem(dbc.NavLink("Cartographie Lizmap", href="/lizmap")),

                                dbc.NavItem(dbc.NavLink("Contrôle Simualtion HEC-RAS ", href="/hecras"))
                                
                            ],
                            navbar=True
                            )
                        ],
                        width={"size":"auto"})
                    ],
                    align="center"),
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
    if n:
        return not is_open
    return is_open




modal=dbc.Modal(
    [
        dbc.ModalHeader("Contrôle de Simulation"),
        dbc.ModalBody(simualtion_run.layout),
        dbc.ModalFooter(
            dbc.Button("Close", id="close-modal", className="ml-auto")
        ),
    ],
    id="modal",
)


# Define the layout of the Dash app
app.layout = html.Div([
    dbc.NavbarSimple(
        dbc.Container([
            dbc.Row([dbc.Col([html.H1(children=["PROTOTYPE Web-MAPPING APPLICATION CHAINE HEC"], id='title_app')], align='center')]),
            dbc.Row([
                dbc.Col([html.Img(id='logo_app', src=app.get_asset_url('logo.png'))],align='left', width=2),
                dbc.Col([dbc.Nav(
                [
                    dbc.NavItem(dbc.NavLink('Interface Graphique', id='tab-1-link', href='graphic', active=True)),
                    dbc.NavItem(dbc.NavLink('Cartographie en temps réel', id='tab-2-link', href='lizmap')),
                    dbc.NavItem(dbc.NavLink('Simulation Run', id='tab-3-link', href='#')),
                ],
                pills=True,
                id='tabs',
            )],align='left')
                
            ])
            
        ]),
        dark=True,
        color="light",
        sticky='top'
    ),
    dbc.Container(id='tabs-content'),
    dcc.Store(id='my-store', storage_type='session'),
    dbc.Container(
        dbc.Row(
            html.P(children=["Powered by Surface Libre ©. All rights Reserved "]), 
            id='footer_tag'
        )
    ),
    modal
])


@app.callback(
    Output('modal', 'is_open'),
    Input('tab-3-link', 'n_clicks'),
    Input('close-modal', 'n_clicks'),
    State('modal', 'is_open')
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

@app.callback(
    Output('tabs-content', 'children'),
    Input('tab-1-link', 'n_clicks'),
    Input('tab-2-link', 'n_clicks'),
    Input('tab-3-link', 'n_clicks')
)
def display_tab(tab1_clicks, tab2_clicks,tab3_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        return graphic_interface.layout
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == 'tab-1-link':
            return graphic_interface.layout
        elif button_id == 'tab-2-link':
            return mapping_lizmap.layout
        elif button_id == 'tab-3-link':
            return modal


if __name__ == '__main__':
    app.run_server(port=5050,debug=True)


# Render the Dash app
@server.route("/")
def index():
    return render_template(
        "index.html",
        dash_url=f"/dash{dash_app.url_base_pathname}"
    )


if __name__ == "__main__":
    server.run()


'''