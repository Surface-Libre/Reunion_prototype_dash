
import win32com.client
import shutil 
import os 
from datetime import datetime, timedelta



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

with open('C:\\Users\\33751\\Desktop\\Prototype_Reunion\\plans_hecras.txt', 'r') as file:
    lines = file.readlines()

values = [line.strip() for line in lines]
prj_path= get_plans(folder_path)[0]

for plan in values:
    import pythoncom
    
    pythoncom.CoInitialize()
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


