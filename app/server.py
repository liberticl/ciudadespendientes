from flask import Flask, request, render_template
from pymongo import MongoClient
from settings import (DEBUG, MONGO_DB, MONGO_CP_DB, CP_STRAVA_COLLECTION)
from codes.plot_maps import *
from utils import get_polygon_middle_point


app = Flask(__name__)

ALLOWED_CITIES = ['Viña del Mar',
                  'Valparaíso',
                  'Villa Alemana',
                  'Quilpué',
                  'Concón']

city = 'Valparaíso, Chile'


# @app.route("/", methods=['GET', 'POST'])
@app.route("/")
def fullscreen():
    # if request.method == 'POST':
    #     city = request.form['city']
    # else:
    #     city = request.args.get('city', 'Viña del Mar')
    # city += ', Chile'
    client = MongoClient(MONGO_DB)
    db = client[MONGO_CP_DB]
    collection1 = db[CP_STRAVA_COLLECTION]
    collection2 = db['ascensores']
    center = get_polygon_middle_point(city, collection1)
    m = color_ride_map(city, center, [2019], collection1, collection2)
    return m.get_root().render()


# @app.route("/search")
# def search():
#     return render_template('search.html', cities=ALLOWED_CITIES)


if __name__ == '__main__':
    if (DEBUG):
        app.run(debug=True, host='0.0.0.0', port=8080)
    else:
        from waitress import serve
        serve(app, host='0.0.0.0', port=8080)
