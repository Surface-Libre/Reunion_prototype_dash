import dash_leaflet as dl
import geopandas as gpd
import json
import os


folder_shapefiles =os.getcwd()+'\\src\\shp\\'


def add_shapfile_stations():

    """
    ddd
    """
    for filename in os.listdir(folder_shapefiles+'stations\\'):
        # check if the file is a .shp file
        if filename.endswith('.shp'):
            shp_stations=gpd.read_file(folder_shapefiles+'stations\\'+filename)

            json_stations=json.loads(shp_stations.to_json())

            stations= dl.GeoJSON(
            data=json_stations, 
            id="geojson",
            options = {
                'radius': 8,
                'fillColor': "lightgreen",
                'color': "black",
                'weight': 1,
                'opacity': 1,
                'fillOpacity': 0.8
            },
            children=[dl.Popup(id="popup_stations")]
            )   
            return stations,shp_stations
        

def add_shapfile_bv():
    for filename in os.listdir(folder_shapefiles+'bv\\'):
        # check if the file is a .shp file
        if filename.endswith('.shp'):
            shp_bv=gpd.read_file(folder_shapefiles+'bv\\'+filename)

            json_bv=json.loads(shp_bv.to_json())

            bv= dl.GeoJSON(
                data=json_bv, 
                id="bv",
                options={"style": {
                    'color': 'blue',
                    'opacity': 0.3,
                    'weight': 1
                }},
                children=[dl.Popup(id="popup_bv")]
            ) 
            return bv,shp_bv
        
def add_shapfile_riv():
    for filename in os.listdir(folder_shapefiles+'rivieres\\'):
        # check if the file is a .shp file
        if filename.endswith('.shp'):
            shp_riv=gpd.read_file(folder_shapefiles+'rivieres\\'+filename)

            json_riv=json.loads(shp_riv.to_json())

            riv= dl.GeoJSON(
                data=json_riv, 
                id="rivers",
                options={"style": {
                    'color': 'red',
                    'opacity': 0.3,
                    'weight': 2
                }}
            )
            return riv,shp_riv
        
    


