import requests
import geopandas as gpd


def get_osm_relation(place: str):
    url = f'https://nominatim.openstreetmap.org/search?q={place}&format=json'
    ans = requests.get(url)
    data = ans.json()

    for element in data:
        if (element['type'] == 'administrative'):
            return element['osm_id']

    return None


def get_place_polygon(place):
    relation = get_osm_relation(place)
    url = f'http://polygons.openstreetmap.fr/get_geojson.py?id={relation}&params=0' # noqa
    ans = requests.get(url)
    gdf = gpd.read_file(ans.text)
    gdf = gdf.explode(index_parts=False)
    return gdf
