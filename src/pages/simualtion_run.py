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
import subprocess



from apps import navigationbar

dash.register_page(__name__, path='/simrun', title="Simulation Run", description="Simulation_run", image='logo.png')

folder_path = 'C:\\Users\\33751\\Downloads\\Modele_Hydrologie_Dashboard\\Modele_Hydrologie_Dashboard\\'

values_timestep= {"15min": 'PT5M',"1h": 'PT1H',"3h": 'PT3H',"6h": 'PT6H'}


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


layout = [
    navigationbar.navbar,
    html.Br(),
    dbc.Container(
        dbc.Card(
            [
                dbc.CardHeader("Run Simulation"),
                dbc.CardBody(
                    [
                        dbc.Container(
                            id='cont_run',
                            children=[
                                dbc.Row([
                                    html.Div(
                                        id='output_ras_folder',
                                        children=['Projet HEC-RAS choisi: {}'.format(get_plans(folder_path)[0])],
                                        className="col-12 mb-3"
                                    ),
                                    html.Div(
                                        [
                                            html.H6('Selectionner les plans du projet HEC-RAS à exécuter:', className='h6'),
                                            dcc.Dropdown(
                                                id='check-plans',
                                                options=options_chek,
                                                value=[],
                                                multi=True,
                                                persistence=True,
                                                className="w-100"
                                            )
                                        ],
                                        className="col-12"
                                    )
                                ]),
                                html.Br(),
                                dbc.Row([
                                    dcc.Tabs([
                                        dcc.Tab(label='Mode Automatique', children=[
                                            html.Br(),
                                            html.H6("Selectionner le pas du temps pour l'automatisation de simulation' :", className='h6'),
                                            dcc.Dropdown(
                                                id='interval-dropdown-auto',
                                                options=[
                                                    {'label': '15 minutes', 'value': '15min'},
                                                    {'label': '1 heure', 'value': '1h'},
                                                    {'label': '3 heures', 'value': '3h'},
                                                    {'label': '6 heures', 'value': '6h'}
                                                ],
                                                value='15min',
                                                persistence=True,
                                                className="w-100"
                                            ),
                                            html.Br(),
                                            html.Div([
                                                html.Button('Run simulation', id='auto_run_simulation_btn', n_clicks=0, className="btn btn-primary"),
                                                html.Br(),
                                                html.H5(html.Div(id='auto_simulation_output'), className='h5')
                                            ])
                                        ]),
                                        dcc.Tab(label='Mode Rejeu (Manuel)', children=[
                                            html.Div([
                                                html.Div([
                                                    html.Label("Nombre de jours"),
                                                    dcc.Input(
                                                        id="nb-jour-input",
                                                        type="text",
                                                        placeholder="Nombre de jours",
                                                        persistence=True,
                                                        className="form-control"
                                                    )
                                                ]),
                                                html.Br(),
                                                html.Div([
                                                    html.Label("t0: date"),
                                                    dcc.DatePickerSingle(
                                                        id='date-picker',
                                                        className='form-control my-datepicke',
                                                        initial_visible_month=datetime.today(),
                                                        date=datetime.today()
                                                    )
                                                ]),
                                                html.Br(),
                                                html.Div([
                                                    html.Label("Heure: (Heure Locale)"),
                                                    dcc.Dropdown(
                                                        id='time-dropdown',
                                                        options=[{'label': f'{i:02d}:{j:02d}', 'value': f'{i:02d}:{j:02d}'}
                                                                 for i in range(1, 25) for j in range(0, 60, 15)],
                                                        value='01:00',
                                                        className="w-100"
                                                    )
                                                ])
                                            ]),
                                            html.Br(),
                                            html.Button('Run simulation', id='man_run_simulation_btn', n_clicks=0, className="btn btn-primary"),
                                            html.Br(),
                                            html.H6(html.Div(id='man_simulation_output'), className='h6')
                                        ])
                                    ])
                                ])
                            ],
                            className="container"
                        )
                    ],
                    className="card-body"
                )
            ],
            color="secondary",
            outline=True,
            className="card",
            style={
                "width": "70%",
                "margin": "auto",
                "marginTop": "10%"
            }
        )
    )
]



@dash.callback(
    [Output('auto_simulation_output', 'children')],
    [Input('auto_run_simulation_btn', 'n_clicks'),
     Input('check-plans', 'value'),
     Input('interval-dropdown-auto','value')],
    prevent_initial_call=True
)
def auto_run_button_click(n_clicks, values_plans,timestep):
    """
    Callback function to handle the click event of the auto run simulation button.

    Args:
        n_clicks (int): The number of times the button has been clicked.
        values (list): The selected values from the check-plans dropdown.

    Returns:
        list: A list containing the output message.
    """
    if n_clicks > 0:

        with open('selected_interval.txt', 'w') as file:
            pass


        with open('plans_hecras.txt', 'w') as file:
            for value in values_plans:
                file.write(f"{value}\n")

        
        interval = values_timestep[timestep]
        command = "{"+f"""$taskName = 'auto_simulation'; $task = Get-ScheduledTask -TaskName $taskName; $trigger = $task.Triggers[0]; $trigger.Repetition.Interval = '{interval}'; $trigger.StartBoundary = (Get-Date).AddMinutes(0).ToString(\'yyyy-MM-ddTHH:mm:ss\'); Set-ScheduledTask -TaskName $taskName -Trigger $trigger -Verbose"""+"}"

        subprocess.run(['powershell.exe', '-Command', 'Start-Process', 'powershell.exe', '-ArgumentList', f'{command}', '-Verb', 'RunAs', '-WindowStyle Hidden'])
        return [' La simulation a été exécutée avec succès.']
    else:
        return [""]


@dash.callback(
    [Output('man_simulation_output', 'children')],
    [Input('man_run_simulation_btn', 'n_clicks'),
     Input('nb-jour-input', 'value'),
     Input('date-picker', 'date'),
     Input('time-dropdown', 'value'),
     Input('check-plans', 'value')],
    prevent_initial_call=True
)
def man_run_button_click(n_clicks, nb_jour, date_picked, time_picked, values):
    """
    Callback function to handle the click event of the manual run simulation button.

    Args:
        n_clicks (int): The number of times the button has been clicked.
        nb_jour (str): The number of days entered by the user.
        date_picked (str): The t0 date entered by the user.
        time_pciked (str): The t0 time entered by the user.
        values (list): The selected values of plans from the check-plans dropdown.

    Returns:
        list: A list containing the output message.
    """

    dt_string = f'{date_picked} {time_picked}'

    now = datetime.strptime(dt_string,"%Y-%m-%d %H:%M")

    current_date = now.strftime("%m/%d/%Y")
    current_time = now.strftime("%H:%M")

    hindcast = now - timedelta(hours=24*int(nb_jour))
    hindcast_date = hindcast.strftime("%m/%d/%Y")
    hindcast_time = hindcast.strftime("%H:%M")

    forecast = now + timedelta(hours=48)
    forecast_date = forecast.strftime("%m/%d/%Y")
    forecast_time = forecast.strftime("%H:%M")


    if n_clicks > 0:
        print(values)
        print("Simulation Date=" + hindcast_date + ',' + hindcast_time.replace(':', '') + ',' + forecast_date + ',' + forecast_time.replace(':', '') + "\n")
        import win32com.client

        for plan in values:
            import pythoncom
            # Call CoInitialize to initialize the COM library
            pythoncom.CoInitialize()

            hec = win32com.client.Dispatch("RAS631.HECRASController")
            hec.Project_Open(prj_path)

            hec.Plan_SetCurrent(plan)
            strPlanfile = hec.CurrentPlanFile()
            strNewPlanfile = strPlanfile[:strPlanfile.index(".") + 1] + 'temp' + strPlanfile[strPlanfile.index(".") + 1:]

            with open(strPlanfile, 'r') as input_file, open(strNewPlanfile, 'w') as output_file:
                for line in input_file:
                    if "Simulation Date=" in line:
                        output_file.write("Simulation Date=" + hindcast_date + ',' + hindcast_time.replace(':', '') + ',' + 
                                          forecast_date + ',' + forecast_time.replace(':', '') + "\n")
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
        return ['La simulation a été exécutée avec succès.']
    else:
        return ['']

