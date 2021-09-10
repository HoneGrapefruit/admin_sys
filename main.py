"""
main.py - 主程序（项目入口）

路由 ---> 视图（view）函数

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
from api import bp
from utils import random_captcha_code, get_mysql_connection, random_secret_key, check_login

app = flask.Flask(__name__)
CORS(app)

# 注册蓝图
app.register_blueprint(bp)

# app.config['SECRET_KEY'] = random_secret_key()
app.secret_key = random_secret_key()
# app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.permanent_session_lifetime = timedelta(days=7)


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
    # 更好的做法是在用户浏览器中保存一个身份令牌（token） ---> JWT（JSON Web Token）
    session['user_id'] = user_dict['user_id']
    session.permanent = True
    nickname, avatar = user_dict['nickname'], user_dict['avatar']
    return {'code': 10000, 'message': '登录成功', 'nickname': nickname, 'avatar': avatar}


@app.route('/logout')
@check_login
def logout():
    session.clear()
    return {'code': 10003, 'message': '退出登录'}


if __name__ == '__main__':
    app.run(port=8000, debug=True)
