import geopandas as gpd
import folium
from .apis import get_place_polygon
from .mongodb import points_inside
from shapely.geometry import LineString, Point, Polygon
from shapely.geometry import box


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
    cursor = collection.find(
        points_inside,
        {'_id': 0, **dict.fromkeys(projection, 1)})

    data = list(cursor)
    parsed_data = []
    for item in data:
        parsed_proj = {}
        for key in projection:
            if key != 'geometry':
                parsed_proj.update({key: item[key]})
            else:
                parsed_proj.update(
                    {'geometry': Point(item[key]['coordinates'])})
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


def get_city_bounds(city, only_bounds=False):
    gdf_city = get_place_polygon(city).to_crs('EPSG:3857')
    gdf_city['area'] = gdf_city['geometry'].area
    data = gdf_city[gdf_city['area'] == gdf_city['area'].max()]

    if (only_bounds):
        data = data[['geometry']].to_crs(epsg='4326').total_bounds
        return box(*data)
    else:
        data = data.to_crs(epsg='4326').to_dict()
        return data['geometry'][0]


def city_ride_map(city, center, collection):
    coords = list(Polygon(get_city_bounds(city)).exterior.coords)
    coords = [[round(x, 6), round(y, 6)] for x, y in coords]
    coords = [coords + [coords[0]]]
    inside = points_inside
    inside['middlePoint']['$geoWithin']['$geometry']['coordinates'] = coords
    projection = ['year', 'geometry']
    cursor = collection.find(
        inside,
        {'_id': 0, **dict.fromkeys(projection, 1)})

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

    mapa = folium.Map(location=center,
                      zoom_start=13,    # Ver si es factible automatizar
                      control_scale=True
                      )
    geojson_data = gdf.to_json()
    folium.GeoJson(geojson_data).add_to(mapa)
    return mapa


def color_ride_map(city, center, years, collection):
    coords = list(Polygon(get_city_bounds(city)).exterior.coords)
    coords = [[round(x, 6), round(y, 6)] for x, y in coords]
    coords = [coords + [coords[0]]]
    inside = points_inside[0]['$match']
    inside['middlePoint']['$geoWithin']['$geometry']['coordinates'] = coords
    inside['year']['$in'] = years
    projection = ['year', 'total_trip_count', 'geometry']
    del coords
    cursor = collection.find(
        inside,
        {'_id': 0, **dict.fromkeys(projection, 1)})

    mapa = folium.Map(
        location=center,
        zoom_start=13,
        control_scale=True,
        tiles='CartoDB positron')

    for item in cursor:
        coords = [[lat, lon] for lon, lat in item['geometry']['coordinates']]
        total_trip_count = item['total_trip_count']
        line_color = 'blue'

        if total_trip_count > 10000:
            line_color = 'red'
        elif total_trip_count > 1000:
            line_color = 'orange'
        elif total_trip_count > 200:
            line_color = 'yellow'

        folium.PolyLine(locations=coords,
                        color=line_color,
                        tooltip=f"Total Trip Count: {total_trip_count}"
                        ).add_to(mapa)

    return mapa
