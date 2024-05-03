from flask import Flask, request, redirect, url_for, render_template
from pymongo import MongoClient
from settings import (DEBUG, MONGO_DB, MONGO_CP_DB, CP_STRAVA_COLLECTION)
from codes.plot_maps import get_city_data, color_ride_map


app = Flask(__name__)

ALLOWED_YEARS = [2019, 2020, 2021, 2022, 2023]

ALLOWED_CITIES = ['Viña del Mar',
                  'Valparaíso',
                  'Villa Alemana',
                  'Quilpué',
                  'Concón']

city = 'Valparaíso, Chile'


# TO-DO: mejora de index.html
@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        years = request.form.getlist("periodo")
        cities = request.form.getlist("comunas")

        return redirect(url_for("show_data", periodo=years, comunas=cities))

    return render_template("index.html",
                           periodo=ALLOWED_YEARS,
                           comunas=ALLOWED_CITIES)


@app.route("/mapa")
def show_data():

    years = [int(year) for year in request.args.getlist("periodo")]
    cities = [city + ', Chile' for city in request.args.getlist("comunas")]

    client = MongoClient(MONGO_DB)
    db = client[MONGO_CP_DB]
    collection = db[CP_STRAVA_COLLECTION]
    city = get_city_data(cities[0])
    city_bounds = city[0]
    city_reference = city[1]
    m = color_ride_map(city_bounds, city_reference, years, collection)

    return m.get_root().render()


# @app.route("/fullscreen")
# def fullscreen():
#     client = MongoClient(MONGO_DB)
#     db = client[MONGO_CP_DB]
#     collection1 = db[CP_STRAVA_COLLECTION]
#     collection2 = db['ascensores']
#     center = get_polygon_middle_point(city, collection1)
#     m = color_ride_map2(city, center, [2019], collection1, collection2)
#     return m.get_root().render()

if __name__ == '__main__':
    if (DEBUG):
        app.run(debug=True, host='0.0.0.0', port=8080)
    else:
        from waitress import serve
        serve(app, host='0.0.0.0', port=8080)
