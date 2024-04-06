import os
import folium
import requests
import pandas as pd
import geopandas as gpd
from zipfile import ZipFile
from pymongo import MongoClient
from shapely.geometry import LineString
from settings import (MONGO_DB, MONGO_CP_DB, CP_STRAVA_COLLECTION,
                      DATA_DIR, DEBUG)


# Creates the mongodb files to upload
def create_features(geodata, max=10):
    features = []
    if DEBUG:
        geodata = geodata.head(max)

    for feature in geodata.iterfeatures():
        prop = feature.pop('properties', None)
        if prop:
            feature.update(prop)
        feature.pop('id', None)
        feature.pop('type', None)
        feature.pop('edge_uid', None)
        feature.pop('osm_reference_id', None)
        features.append(feature)

    return features


# Get data from Strava's ZIP file.
# - SHP file for geometry objects
# - CSV file for getting Strava info
def strava_to_mongo(stravazipfile, collection):
    print(f'Extrayendo los datos de {stravazipfile}')
    path = os.getcwd() + os.sep + DATA_DIR + os.sep + stravazipfile

    with ZipFile(path, 'r') as zip:
        files = zip.infolist()
        shpfile = [file.filename for file in files if 'shp' in file.filename][0] # noqa
        csvfile = [file for file in files if 'csv' in file.filename][0]

        geodata = gpd.read_file(path + '!' + shpfile, )
        with zip.open(csvfile) as csv:
            data = pd.read_csv(csv, low_memory=False)

    print('Generando elementos para subir a mongodb')
    merged_df = pd.merge(geodata, data,
                         how='inner', left_on='edgeUID', right_on='edge_uid')

    features = create_features(merged_df)
    print(f'Insertando {len(features)} elementos en mongodb')
    collection.insert_many(features, ordered=False)


# def points_to_cities():



def plot_data(collection):
    query = {'year': 2023}
    projection = ['year', 'geometry']
    cursor = collection.find(query, {'_id': 0, **dict.fromkeys(projection, 1)})

    data = list(cursor)
    parsed_data = []
    for item in data:
        parsed_proj = {}
        for key in projection:
            if key != 'geometry':
                parsed_proj.update({key: item[key]})
            else:
                parsed_proj.update({key: LineString(item[key]['coordinates'])})
        parsed_data.append(parsed_proj)

    gdf = gpd.GeoDataFrame(parsed_data)

    mapa = folium.Map(location=(-33.049689, -71.621202),    # Mi casa
                      zoom_start=13,    # Ver si es factible automatizar
                      control_scale=True
                      )
    geojson_data = gdf.to_json()
    folium.GeoJson(geojson_data).add_to(mapa)
    return mapa


if __name__ == '__main__':
    client = MongoClient(MONGO_DB)
    db = client[MONGO_CP_DB]
    collection = db[CP_STRAVA_COLLECTION]

    # import time
    # start = time.time()
    # plot_data(collection)
    # end = time.time()
    # print(f'Mapa generado en {end - start} segundos\n')

    # for year in [2021, 2022, 2023]:
    #     start = time.time()
    #     strava_to_mongo(f'{year}.zip')
    #     end = time.time()
    #     print(f'Datos importados a mongodb en {end - start} segundos\n')
