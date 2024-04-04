from flask import Flask
from pymongo import MongoClient
from settings import (MONGO_DB, MONGO_CP_DB, CP_STRAVA_COLLECTION)
from utils import plot_data


app = Flask(__name__)


@app.route("/valpo")
def fullscreen():
    client = MongoClient(MONGO_DB)
    db = client[MONGO_CP_DB]
    collection = db[CP_STRAVA_COLLECTION]
    m = plot_data(collection)
    return m.get_root().render()
