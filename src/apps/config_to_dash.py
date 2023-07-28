

config_file = r'C:\Users\33751\Desktop\Prototype_Reunion\configuration.txt'  # Replace with the actual path to your config file

def parse_config_file(file_path):
    config_data = {}
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                config_data[key.strip()] = value.strip()
    return config_data

# Parse the config file and store the pathnames in variables
config_data = parse_config_file(config_file)

# Access the pathnames using the variable names
hec_ras_project_file = config_data['HEC RAS PROJECT FOLDER']
dss_file_simulation = config_data['DSS FILE SIMULATION']
dss_file_observation_data = config_data['DSS FILE OBSERVATION DATA']
dss_file_rainfall_bv=config_data['DSS FILE RAINFALL DATA']

