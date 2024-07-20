from flask import Flask, request, redirect, url_for, render_template, session
from pymongo import MongoClient
from settings import (DEBUG, MONGO_DB, MONGO_CP_DB, CP_STRAVA_COLLECTION,
                      SESSION_KEY, AUTH_INFO)
from codes.plot_maps import get_city_data, color_ride_map
from utils import get_middle_point
from waitress import serve
# from datetime import datetime


app = Flask(__name__)
app.secret_key = SESSION_KEY

ALLOWED_YEARS = [2019, 2020, 2021, 2022, 2023]

ALLOWED_CITIES = ['Viña del Mar',
                  'Valparaíso',
                  'Villa Alemana',
                  'Quilpué',
                  'Concón']

city = 'Valparaíso, Chile'
# users = {USERNAME: PASSWORD}


@app.before_request
def before_request():
    request.path_name = request.path


# TO-DO: mejora de index.html
@app.route('/', methods=['GET', 'POST'])
def index():
    if 'username' in session:
        if request.method == 'POST':
            years = request.form.getlist('periodo')
            cities = request.form.getlist('comunas')

            return redirect(url_for('show_data',
                                    periodo=years,
                                    comunas=cities))

        return render_template('index.html',
                               periodo=ALLOWED_YEARS,
                               comunas=ALLOWED_CITIES)
    else:
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in AUTH_INFO and AUTH_INFO[username] == password:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('error.html')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route("/mapa")
def show_data():
    if 'username' in session:
        years = [int(year) for year in request.args.getlist("periodo")]
        cities = [city + ', Chile' for city in request.args.getlist("comunas")]

        client = MongoClient(MONGO_DB)
        db = client[MONGO_CP_DB]
        collection = db[CP_STRAVA_COLLECTION]
        all_bounds = []
        all_references = []
        # start = datetime.now()
        for city in cities:
            city_data = get_city_data(city)
            all_bounds.append(city_data[0])
            all_references.append(city_data[1])
        # print(f'| Búsqueda de ciudades en API de OpenStreetMap | {(datetime.now() - start).total_seconds()} |') # noqa
        # start = datetime.now()
        center = get_middle_point(all_references)
        # print(f'| Cálculo de punto medio de la comuna | {(datetime.now() - start).total_seconds()} |') # noqa
        # start = datetime.now()
        m, s = color_ride_map(all_bounds, center, years, collection)
        # print(f'| Obtención del mapa HTML con Folium | {(datetime.now() - start).total_seconds()} |') # noqa
        # dynamic = m.get_root().render()
        # start = datetime.now()
        dynamic = m._repr_html_()
        # print(f'| Renderizado del mapa HTML en Flask | {(datetime.now() - start).total_seconds()} |') # noqa
        stats = [round(x) for x in s]
        return render_template('mapa.html',
                               stats=stats,
                               dynamic_content=dynamic)
    else:
        return redirect(url_for('login'))


if __name__ == '__main__':
    if (DEBUG):
        app.run(debug=True, host='0.0.0.0', port=8080)
    else:
        serve(app, host='0.0.0.0', port=8080)
