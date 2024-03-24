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
# print(DEBUG)
