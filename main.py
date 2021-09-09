"""
main.py - 主程序（项目入口）

Author: Hao
Date: 2021/9/9
"""
import functools
import hashlib
from datetime import timedelta

import flask
import pymysql.cursors
from flask import redirect, session, request, make_response
from flask_cors import CORS

import captcha
from utils import random_captcha_code, get_mysql_connection

app = flask.Flask(__name__)
app.secret_key = '1Qaz2Wsx'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(seconds=1800)
CORS(app)


def check_login(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return redirect('/static/lyear_pages_login.html')
        return func(*args, **kwargs)

    return wrapper


@app.route('/')
@check_login
def show_index():
    return redirect('/static/index.html')


@app.route('/captcha')
def get_captcha_image():
    cap = captcha.Captcha.instance()  # type: captcha.Captcha
    captcha_code = random_captcha_code()
    session['captcha_code'] = captcha_code.lower()
    cap_image_data = cap.generate(captcha_code)
    resp = make_response(cap_image_data)
    resp.headers['content-type'] = 'image/png'
    return resp


@app.route('/login', methods=['POST', ])
def login():
    params = request.json
    captcha_from_user = params.get('captcha').lower()
    captcha_from_sess = session.get('captcha_code')
    if captcha_from_sess != captcha_from_user:
        return {'code': 10001, 'message': '验证码错误'}
    username = params.get('username')
    password = params.get('password')
    password = hashlib.md5(password.encode()).hexdigest()
    conn = get_mysql_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(
                'select user_id, nickname, avatar from tb_user where username=%s and userpass=%s',
                (username, password)
            )
            user_dict = cursor.fetchone()
    finally:
        conn.close()
    if user_dict is None:
        return {'code': 10002, 'message': '用户名或密码错误'}
    session['user_id'] = user_dict['user_id']
    session.permanent = True
    nickname, avatar = user_dict['nickname'], user_dict['avatar']
    return {'code': 10000, 'message': '登录成功', 'nickname': nickname, 'avatar': avatar}


@app.route('/logout')
@check_login
def logout():
    session.pop('user_id')
    return {'code': 10003, 'message': '退出登录'}


if __name__ == '__main__':
    app.run(port=8000, debug=True)