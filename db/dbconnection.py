from dotenv import load_dotenv
from os import environ, path
from psycopg2 import connect, OperationalError


dotenv_path = path.abspath(path.join(path.dirname(__file__), '..', '.env'))
if path.exists(dotenv_path):
    load_dotenv(dotenv_path)


if environ.get('TEST') == "False":
    db_settings = {"database": environ.get('POSTGRES_TYPE'),
                   "user": environ.get('POSTGRES_USER'),
                   "password": environ.get('POSTGRES_PASSWORD'),
                   "host": environ.get('POSTGRES_HOST'),
                   "port": int(environ.get('POSTGRES_PORT'))}
else:
    db_settings = {"database": environ.get('POSTGRES_TEST_DB'),
                   "user": environ.get('POSTGRES_USER'),
                   "password": environ.get('POSTGRES_PASSWORD'),
                   "host": environ.get('POSTGRES_TEST_HOST'),
                   "port": int(environ.get('POSTGRES_TEST_PORT'))}

# Database
connection = connect(**db_settings)
cursor = connection.cursor()

