import base64
import functools
import os
import random
import string
from functools import partial

import pymysql
from flask import session, redirect

DB_HOST = os.environ.get('DB_HOST') or 'localhost'
DB_PORT = os.environ.get('DB_PORT') or '3306'
DB_USER = os.environ.get('DB_USER') or 'root'
DB_PASS = os.environ.get('DB_PASS') or '123456'
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


def random_captcha_code(length=4):
    """生成随机验证码"""
    all_chars = string.ascii_letters + string.digits
    return ''.join(random.choices(all_chars, k=length))


def random_secret_key(length=24):
    """生成随机会话密钥"""
    random_key = ''.join(random.choices(string.printable, k=length))
    return base64.b64encode(random_key.encode()).decode()


def check_login(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/static/lyear_pages_login.html')
        return func(*args, **kwargs)

    return wrapper