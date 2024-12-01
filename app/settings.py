import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB info
MONGO_DB = os.environ.get('MONGO_DB')
MONGO_CP_DB = os.environ.get('MONGO_CP_DB')
CP_STRAVA_COLLECTION = os.environ.get('CP_STRAVA_COLLECTION')

# Other
DATA_DIR = os.environ.get('DATA_DIR')
DEBUG = os.environ.get('DEBUG').capitalize() == 'True'
SESSION_KEY = os.environ.get('SESSION_KEY')
FLASK_ENV = os.environ.get('FLASK_ENV')

# Users
USERNAME = os.environ.get('ADMINUSER')
PASSWORD = os.environ.get('PASSWORD')
STRAVAUSER = os.environ.get('STRAVAUSER')
STRAVAPSS = os.environ.get('STRAVAPSS')
TESTUSER = os.environ.get('TESTUSER')
TESTPSS = os.environ.get('TESTPSS')

AUTH_INFO = {
    USERNAME: PASSWORD,
    STRAVAUSER: STRAVAPSS,
    TESTUSER: TESTPSS
}
# print(DEBUG)
