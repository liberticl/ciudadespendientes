import requests
import geopandas as gpd


# def get_graph(place,mode = 'all', only_edges = True):
#     graph = ox.graph_from_place(place, network_type = mode)
#     if(only_edges):
#         _,edges = ox.graph_to_gdfs(graph, edges = True,fill_edge_geometry=True, clean_periphery = True)
#         return edges
#     return graph

def get_osm_relation(place:str):
    url = f'https://nominatim.openstreetmap.org/search?q={place}&format=json'
    ans = requests.get(url)
    data = ans.json()
    
    for element in data:
        if(element['type'] == 'administrative'):
            return element['osm_id']
        
    return None
    
def get_place_polygon(place):
    try:
        relation = get_osm_relation(place)
        url = f'http://polygons.openstreetmap.fr/get_geojson.py?id={relation}&params=0'
        ans = requests.get(url)
        gdf = gpd.read_file(ans.text)
        # return gdf
        gdf = gdf.explode(index_parts = False)
        return gdf
    except:
        return -1
    
# print(get_place_polygon('Valparaíso, Valparaíso, Chile'))