import os
from functools import partial

import pymysql

DB_HOST = os.environ.get('DB_HOST') or 'localhost'
DB_PORT = os.environ.get('DB_PORT') or '3306'
DB_USER = os.environ.get('DB_USER') or 'guest'
DB_PASS = os.environ.get('DB_PASS') or 'Guest.618'
DB_NAME = os.environ.get('DB_NAME') or 'data_viz'
DB_CHAR = os.environ.get('DB_CHAR') or 'utf8mb4'

db_config = {
    'host': DB_HOST,
    'port': int(DB_PORT),
    'user': DB_USER,
    'password': DB_PASS,
    'charset': DB_CHAR
}
connect_mysql = partial(pymysql.connect, **db_config)


def get_mysql_connection(database=DB_NAME):
    return connect_mysql(database=database)
