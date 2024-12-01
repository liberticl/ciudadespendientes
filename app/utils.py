import os
import pandas as pd
import geopandas as gpd
from codes.mongodb import middle_points_aggregate
from zipfile import ZipFile
from pymongo import MongoClient, UpdateOne
from app.settings import (MONGO_DB, MONGO_CP_DB, CP_STRAVA_COLLECTION,
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


# Get middle point for all lines
def create_middle_points(collection):
    pipeline = middle_points_aggregate
    cursor = collection.aggregate(pipeline)
    data = list(cursor)

    update_operation = [
        {
            'filter': {'_id': result['_id']},
            'update': {'$set': {'middlePoint': result['middlePoint']}}
        }
        for result in data
    ]

    collection.bulk_write([UpdateOne(**op) for op in update_operation])


# Get middle point of city reference
def get_middle_point(references):
    references_sum = [0, 0]

    for ref in references:
        references_sum = [x + y for x, y in zip(references_sum, ref)]

    return tuple([element / len(references) for element in references_sum])


if __name__ == '__main__':
    # import time
    client = MongoClient(MONGO_DB)
    db = client[MONGO_CP_DB]
    collection = db[CP_STRAVA_COLLECTION]
    # city = 'Viña del Mar, Chile'
    # center = get_polygon_middle_point(city, collection)
    # color_ride_map(city, center, collection)

    # print('Importando datos a MongoDB...')
    # for year in [2019]:
    #     start = time.time()
    #     strava_to_mongo(f'{year}.zip', collection)
    #     end = time.time()
    #     print(f'Datos importados a mongodb en {end - start} segundos\n')

    # print(f'Creando puntos medios...')
    # create_middle_points(collection)
    # print(f'Finalizado!')
    client.close()
