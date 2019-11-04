import os
from datetime import timedelta

SECRET_KEY = 'secret-gift-points'
PERMANENT_SESSION_LIFETIME = timedelta(minutes=10)

PROJECT_ID = 'gift-points'

CLOUDSQL_USER = 'root'
CLOUDSQL_PASSWORD = 'password'
CLOUDSQL_DATABASE = 'gift'
CLOUDSQL_CONNECTION_NAME = 'gift-points:us-central1:myinstance'
LOCAL_SQLALCHEMY_DATABASE_URI = (
    'mysql+pymysql://{user}:{password}@127.0.0.1:3306/{database}').format(
        user=CLOUDSQL_USER, password=CLOUDSQL_PASSWORD,
        database=CLOUDSQL_DATABASE)
LIVE_SQLALCHEMY_DATABASE_URI = (
    'mysql+pymysql://{user}:{password}@localhost/{database}'
    '?unix_socket=/cloudsql/{connection_name}').format(
        user=CLOUDSQL_USER, password=CLOUDSQL_PASSWORD,
        database=CLOUDSQL_DATABASE, connection_name=CLOUDSQL_CONNECTION_NAME)

if os.environ.get('GAE_INSTANCE'):
    SQLALCHEMY_DATABASE_URI = LIVE_SQLALCHEMY_DATABASE_URI
else:
    SQLALCHEMY_DATABASE_URI = LOCAL_SQLALCHEMY_DATABASE_URI
