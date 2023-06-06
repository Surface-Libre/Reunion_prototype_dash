"""
This script defines the layout for the simulation run controller of preconfigured HEc-Ras project.
"""
from dash import dcc
from dash import html
from datetime import datetime, timedelta
from dash.dependencies import Input, Output
import os
import dash_bootstrap_components as dbc
import shutil
import os
import dash

from apps import navigationbar

dash.register_page(__name__, path='/simrun', title="Simulation Run", description="Simulation_run", image='logo.png')

folder_path = 'C:\\Users\\33751\\Downloads\\Modele_Hydrologie_Dashboard\\Modele_Hydrologie_Dashboard\\'


def get_plans(folder_path):
    """
    Get the HEC-RAS project files and plan names from the specified folder path.

    Args:
        folder_path (str): The path to the folder containing HEC-RAS project files.

    Returns:
        tuple: A tuple containing the path to the HEC-RAS project file and a list of plan names.
    """
    import win32com.client
    import pythoncom
    # Call CoInitialize to initialize the COM library
    pythoncom.CoInitialize()
    global prj_path
    global options_chek

    hec = win32com.client.Dispatch("RAS631.HECRASController")  # initialize the controller of HEC-RAS software (version 5.0.1)

    for filename_prj in os.listdir(folder_path):
        # check if the file is a CSV file
        if filename_prj.endswith('.prj'):
            prj_path = os.path.normpath(os.path.join(folder_path, filename_prj))

            hec.Project_Open(prj_path)
            options_chek = list(hec.Plan_Names()[1])
            print(options_chek)

            hec.QuitRas()
            return prj_path, options_chek


def get_date_time():
    """
    Get the current date and time, hindcast date and time, and forecast date and time.

    Returns:
        tuple: A tuple containing the current date, current time, hindcast date, hindcast time, forecast date, and forecast time.
    """
    now = datetime.now()
    current_date = now.strftime("%m/%d/%Y")
    current_time = now.strftime("%H:%M")

    hindcast = now - timedelta(hours=24)
    hindcast_date = hindcast.strftime("%m/%d/%Y")
    hindcast_time = hindcast.strftime("%H:%M")

    forecast = now + timedelta(hours=48)
    forecast_date = forecast.strftime("%m/%d/%Y")
    forecast_time = forecast.strftime("%H:%M")

    return current_date, current_time, hindcast_date, hindcast_time, forecast_date, forecast_time


controller = [
    dbc.CardHeader("Run Simulation"),
    dbc.CardBody(
        [
            dbc.Container(id='cont_run', children=[
                dbc.Row([html.H2(children='PROJET HEC-RAS')]),
                dbc.Row([
                    html.Div(id='output_ras_folder',
                             children=[' Choosen HEC-RAS project :  {}'.format(get_plans(folder_path)[0])]),
                    html.H3('Select  HEC-RAS palns to run:'),
                    dcc.Dropdown(id='check-plans', options=options_chek, value=[], multi=True, persistence=True)

                ]),
                dbc.Row([dcc.Tabs([
                    dcc.Tab(label='Automatic mode', children=[
                        html.Div([
                            html.Button('Run simulation', id='auto_run_simulation_btn', n_clicks=0),
                            html.Div(id='auto_simulation_output')
                        ])
                    ]),
                    dcc.Tab(label='Manual mode', children=[
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Label("Start Date (MM/DD/YYYY):"),
                                        dcc.Input(id="manual-mode-start-date", type="text",
                                                  placeholder="MM/DD/YYYY", persistence=True),
                                        html.Label("Start Time (HHMM):"),
                                        dcc.Input(id="manual-mode-start-time", type="text",
                                                  placeholder="HHMM", persistence=True),
                                    ]
                                    ,
                                ),
                                html.Div(
                                    [
                                        html.Label("End Date (MM/DD/YYYY):"),
                                        dcc.Input(id="manual-mode-end-date", type="text",
                                                  placeholder="MM/DD/YYYY", persistence=True),
                                        html.Label("End Time (HHMM):"),
                                        dcc.Input(id="manual-mode-end-time", type="text",
                                                  placeholder="HHMM", persistence=True),
                                    ],

                                ),
                                html.Button('Run simulation', id='man_run_simulation_btn', n_clicks=0),
                                html.H4(html.Div(id='man_simulation_output'))
                            ]
                        ),
                    ],

                    )])

                ])
                ])
        ]
    )
]

layout = [navigationbar.navbar,
          html.Br(),
          dbc.Card(
              controller,
              color="secondary",
              outline=True,
              style={
                  "width": "50%",
                  "left": "25%",
                  "top": "10%",
                  "position": "absolute",
                  "align": "center"
              }
          )
]


@dash.callback(
    [Output('auto_simulation_output', 'children')],
    [Input('auto_run_simulation_btn', 'n_clicks'),
     Input('check-plans', 'value')]
)
def auto_run_button_click(n_clicks, values):
    """
    Callback function to handle the click event of the auto run simulation button.

    Args:
        n_clicks (int): The number of times the button has been clicked.
        values (list): The selected values from the check-plans dropdown.

    Returns:
        list: A list containing the output message.
    """
    if n_clicks > 0:
        print(values)
        import win32com.client
        print(get_date_time())
        for plan in values:
            import pythoncom
            # Call CoInitialize to initialize the COM library
            pythoncom.CoInitialize()
            print(plan)
            print(prj_path)
            hec = win32com.client.Dispatch("RAS631.HECRASController")
            hec.Project_Open(prj_path)

            hec.Plan_SetCurrent(plan)
            strPlanfile = hec.CurrentPlanFile()
            strNewPlanfile = strPlanfile[:strPlanfile.index(".") + 1] + 'temp' + strPlanfile[strPlanfile.index(".") + 1:]

            with open(strPlanfile, 'r') as input_file, open(strNewPlanfile, 'w') as output_file:
                for line in input_file:
                    if "Simulation Date=" in line:
                        output_file.write(
                            "Simulation Date=" + get_date_time()[2] + ',' + get_date_time()[3].replace(':', '') + ',' +
                            get_date_time()[4] + ',' + get_date_time()[5].replace(':', '') + "\n")
                    else:
                        output_file.write(line)

            shutil.copy(strNewPlanfile, strPlanfile)
            os.remove(strNewPlanfile)

            with open(strPlanfile, 'r') as f:
                contents = f.read()
                print(contents)

            print('choosen plan :' + plan)
            hec.Compute_HideComputationWindow()
            NMsg, TabMsg, block = None, None, True
            v1, NMsg, TabMsg, v2 = hec.Compute_CurrentPlan(NMsg, TabMsg, block)

            hec.QuitRas()
        return ['Function executed successfully.']
    else:
        return ['Function did not be executed successfully.']


@dash.callback(
    [Output('man_simulation_output', 'children')],
    [Input('man_run_simulation_btn', 'n_clicks'),
     Input('manual-mode-start-date', 'value'),
     Input('manual-mode-start-time', 'value'),
     Input('manual-mode-end-date', 'value'),
     Input('manual-mode-end-time', 'value'),
     Input('check-plans', 'value')]
)
def man_run_button_click(n_clicks, start_date, start_time, end_date, end_time, values):
    """
    Callback function to handle the click event of the manual run simulation button.

    Args:
        n_clicks (int): The number of times the button has been clicked.
        start_date (str): The start date entered by the user.
        start_time (str): The start time entered by the user.
        end_date (str): The end date entered by the user.
        end_time (str): The end time entered by the user.
        values (list): The selected values from the check-plans dropdown.

    Returns:
        list: A list containing the output message.
    """
    if n_clicks > 0:
        print(values)
        print("Simulation Date=" + start_date + ',' + start_time + ',' + end_date + ',' + end_time + "\n")
        import win32com.client

        for plan in values:
            import pythoncom
            # Call CoInitialize to initialize the COM library
            pythoncom.Coinitialize()

            

            hec = win32com.client.Dispatch("RAS501.HECRASController")
            hec.Project_Open(prj_path)

            hec.Plan_SetCurrent(plan)
            strPlanfile = hec.CurrentPlanFile()
            strNewPlanfile = strPlanfile[:strPlanfile.index(".") + 1] + 'temp' + strPlanfile[strPlanfile.index(".") + 1:]

            with open(strPlanfile, 'r') as input_file, open(strNewPlanfile, 'w') as output_file:
                for line in input_file:
                    if "Simulation Date=" in line:
                        output_file.write("Simulation Date=" + start_date + ',' + start_time + ',' + end_date + ',' +
                                          end_time + "\n")
                    else:
                        output_file.write(line)

            shutil.copy(strNewPlanfile, strPlanfile)
            os.remove(strNewPlanfile)

            with open(strPlanfile, 'r') as f:
                contents = f.read()
                print(contents)

            print('choosen plan :' + plan)
            
            NMsg, TabMsg, block = None, None, True
            v1, NMsg, TabMsg, v2 = hec.Compute_CurrentPlan(NMsg, TabMsg, block)

            hec.QuitRas()
        return ['Function executed successfully.']
    else:
        return ['']

