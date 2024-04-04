from flask import Flask
from pymongo import MongoClient
from settings import (DEBUG, MONGO_DB, MONGO_CP_DB, CP_STRAVA_COLLECTION)
from utils import plot_data


app = Flask(__name__)


@app.route("/")
def fullscreen():
    client = MongoClient(MONGO_DB)
    db = client[MONGO_CP_DB]
    collection = db[CP_STRAVA_COLLECTION]
    m = plot_data(collection)
    return m.get_root().render()


if __name__ == '__main__':
    app.run(debug=DEBUG, host='0.0.0.0', port=8080)