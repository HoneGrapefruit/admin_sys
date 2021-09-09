"""
main.py - 

Author: Hao
Date: 2021/9/9
"""
import flask
from flask import redirect
from flask_cors import CORS

app = flask.Flask(__name__)
CORS(app)


@app.route('/')
def show_index():
    return redirect('/static/index.html')


if __name__ == '__main__':
    app.run(port=8000, debug=True)
