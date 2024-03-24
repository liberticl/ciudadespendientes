import os
import pandas as pd
import geopandas as gpd
from zipfile import ZipFile
from pymongo import MongoClient
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
def strava_to_mongo(stravazipfile):
    print(f'Extrayendo los datos de {stravazipfile}')
    path = os.getcwd() + os.sep + DATA_DIR + os.sep + stravazipfile
    client = MongoClient(MONGO_DB)
    db = client[MONGO_CP_DB]
    collection = db[CP_STRAVA_COLLECTION]

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


if __name__ == '__main__':
    import time
    for year in [2021, 2022, 2023]:
        start = time.time()
        strava_to_mongo(f'{year}.zip')
        end = time.time()
        print(f'Datos importados a mongodb en {end - start} segundos\n')
