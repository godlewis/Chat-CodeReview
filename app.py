# -*- coding: utf-8 -*-
# @Time    : 2023/7/7 21:03
# @Author  : 南宫乘风
# @Email   : 1794748404@qq.com
# @File    : app.py.py
# @Software: PyCharm
"""
    项目启动文件
"""

import os

from flask import Flask, jsonify, make_response, render_template

from app.chat import chat
from app.git import git
from utils.LogHandler import log
from api.review_api import review_bp
from api.gitlab_api import gitlab_bp

app = Flask(__name__)
app.template_folder = 'web/templates'
app.static_folder = 'web/static'
app.config['debug'] = True

# 蓝图注册
app.register_blueprint(chat, url_prefix='/chat')
app.register_blueprint(git, url_prefix='/git')
app.register_blueprint(review_bp, url_prefix='/api/review')
app.register_blueprint(gitlab_bp, url_prefix='/api/gitlab')


@app.route('/actuator/health', methods=['GET', 'HEAD'])
def health():
    return jsonify({'online': True})


@app.errorhandler(400)
@app.errorhandler(404)
def handle_error(error):
    error_code = str(error.code)
    error_msg = '请求参数不合法' if error.code == 400 else '页面未找到'
    return make_response(jsonify({'code': error_code, 'msg': error_msg}), error.code)


@app.route('/review')
def review_page():
    return render_template('review.html')


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/projects')
def projects():
    return render_template('projects.html')


@app.route('/developers')
def developers():
    return render_template('developers.html')


@app.route('/statistics')
def statistics():
    return render_template('statistics.html')


@app.route('/settings')
def settings():
    return render_template('settings.html')


if __name__ == '__main__':
    os.environ['STABILITY_HOST'] = 'grpc.stability.ai:443'
    app.config['JSON_AS_ASCII'] = False
    log.info('Starting the app...')
    app.run(debug=True, host="0.0.0.0", use_reloader=False)
