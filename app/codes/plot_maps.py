import geopandas as gpd
import folium
from .apis import get_place_polygon
from .mongodb import points_inside
from shapely.geometry import LineString, Point, Polygon


def ride_map(collection):
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


def middle_points_map(collection):
    projection = ['year', 'geometry']
    cursor = collection.find(points_inside, {'_id': 0, **dict.fromkeys(projection, 1)})

    data = list(cursor)
    parsed_data = []
    for item in data:
        parsed_proj = {}
        for key in projection:
            if key != 'geometry':
                parsed_proj.update({key: item[key]})
            else:
                parsed_proj.update({'geometry': Point(item[key]['coordinates'])})
        parsed_data.append(parsed_proj)

    gdf = gpd.GeoDataFrame(parsed_data).head(400)

    mapa = folium.Map(location=(-33.049689, -71.621202),    # Mi casa
                      zoom_start=13,    # Ver si es factible automatizar
                      control_scale=True
                      )
    geojson_data = gdf.to_json()
    folium.GeoJson(geojson_data).add_to(mapa)
    return mapa


def city_map(city):
    gdf_city = get_place_polygon(city).to_crs('EPSG:3857')
    mapa = folium.Map(location=(-33.049689, -71.621202),    # Mi casa
                      zoom_start=13,    # Ver si es factible automatizar
                      control_scale=True
                      )

    gdf_city['area'] = gdf_city['geometry'].area
    data = gdf_city[gdf_city['area'] == gdf_city['area'].max()]
    data = data.to_crs(epsg='4326').to_json()

    folium.GeoJson(data).add_to(mapa)
    return mapa


def get_city_bounds(city):
    gdf_city = get_place_polygon(city).to_crs('EPSG:3857')
    gdf_city['area'] = gdf_city['geometry'].area
    data = gdf_city[gdf_city['area'] == gdf_city['area'].max()]
    data = data.to_crs(epsg='4326').to_dict()
    return data['geometry'][0]

from shapely.wkt import loads
def city_ride_map(city, collection):
    coords = list(Polygon(get_city_bounds(city)).exterior.coords)
    coords = [[round(x,6), round(y,6)] for x,y in coords]
    coords = [coords + [coords[0]]]
    points_inside['middlePoint']['$geoWithin']['$geometry']['coordinates'] = coords
    projection = ['year', 'geometry']
    cursor = collection.find(points_inside, {'_id': 0, **dict.fromkeys(projection, 1)})

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
