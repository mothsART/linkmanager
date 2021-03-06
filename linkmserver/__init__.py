import os
import subprocess
import json

import arrow

from flask import (
    Flask, render_template, abort,
    request, jsonify, g
)
from flask.ext.assets import Environment
# from werkzeug.debug import get_current_traceback
from werkzeug.contrib.cache import SimpleCache
cache = SimpleCache()

from linkmanager import settings
from linkmanager.db import DataBase

app = Flask(__name__)
assets = Environment(app)

if settings.SERVER:
    var_path = '/var/cache/linkmanager'
    if not os.path.exists(var_path):
        os.makedirs(var_path, mode=0o755)
    static_path = os.path.join(var_path, 'static')
    if not os.path.exists(static_path):
        os.symlink(assets.directory, static_path)
    assets.directory = static_path
    assets.url = assets.url[1:]

db = DataBase()
db.editmode = settings.EDITMODE

def read_only(func):
    """ Decorator : get an Unauthorize 403
    when read only's settings is True. """
    def wrapper():
        if settings.READ_ONLY:
            return abort(403)
        return func()
    return wrapper


def is_server(func):
    """ Decorator : get an Unauthorize 403
    when server settings is True """
    def wrapper():
        if settings.SERVER:
            return abort(403)
        return func()
    return wrapper


def launch_browser(BROWSER=False):
    subprocess.call(
        'sleep 0.5;nohup %s http://127.0.0.1:%s/ &' % (
            BROWSER,
            settings.HTTP_PORT
        ),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        shell=True
    )

@app.route("/")
def index():
    return render_template(
        'index.html',
        DEBUG=settings.DEBUG,
        SERVER=settings.SERVER,
        READ_ONLY=settings.READ_ONLY,
        EDITMODE=settings.EDITMODE,
        DELETEDIALOG=settings.DELETEDIALOG,
        nb_links=len(db)
    )
    # try:
    #     error
    # except Exception:
    #     track = get_current_traceback(
    #         skip=1, show_hidden_frames=True,
    #         ignore_system_exceptions=False
    #     )
    #     track.log()
    #     abort(500)

@read_only
@is_server
@app.route("/editmode", methods=['GET', 'POST'])
def editmode():
    if request.method == 'GET':
        return jsonify({'editmode': db.editmode})
    db.editmode = not db.editmode
    return jsonify({'editmode': db.editmode})


@read_only
@app.route("/add", methods=['POST'])
def add():
    fixture = {}
    link = request.form['link']
    fixture[link] = {
        "tags": request.form['tags'].split(),
        "priority": request.form['priority'],
        "description": request.form['description'],
        "title": request.form['title'],
        "init date": str(arrow.now())
    }
    result = db.add_link(json.dumps(fixture))
    return jsonify({'is_add': result})


@read_only
@app.route("/update", methods=['POST'])
def update():
    fixture = {}
    link = request.form['link']
    if request.form['link'] != request.form['newlink']:
        result = db.delete_link(request.form['link'])
        if not result:
            return jsonify({'is_update': False})
        link = request.form['newlink']
    old_link = db.get_link_properties(link)
    fixture[link] = {
        "tags": request.form['tags'].split(),
        "priority": request.form['priority'],
        "description": request.form['description'],
        "title": request.form['title'],
        "init date": old_link['init date'],
        "update date": str(arrow.now())
    }
    if request.form['link'] != request.form['newlink']:
        fixture[link]["init date"] = str(arrow.now())
        fixture[link]["update date"] = old_link['update date']

    result = db.add_link(json.dumps(fixture))
    return jsonify({'is_update': result})


@read_only
@app.route("/delete", methods=['POST'])
def delete():
    result = db.delete_link(request.form['link'])
    return jsonify({'is_delete': result})


@app.route("/search")
def search():
    results = {}
    try:
        tags = next(request.args.items())[0].split()
        links = db.sorted_links(*tags)
    except:
        links = db.sorted_links()
    results = {}
    for l in links:
        properties = db.get_link_properties(l)
        results[l] = properties
    return jsonify(**results)


@app.route("/suggest")
def suggest():
    tags = request.args.get('tags')
    if not tags:
        return jsonify({})
    keywords = tags.split()
    last_keyword = keywords[len(keywords) - 1]
    str_suggestion = ' '.join(keywords[:-1])

    suggestions = {}
    for s in db.complete_tags(last_keyword):
        if s not in keywords:
            suggestions[str_suggestion + ' ' + s] = 10
    return jsonify(**suggestions)


def run(browser=None):
    BROWSER = settings.BROWSER
    if browser:
        BROWSER = browser
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        launch_browser(BROWSER)
    app.debug = settings.DEBUG
    app.run(host=settings.HTTP_HOST, port=settings.HTTP_PORT)
    settings.set_user_conf(WEBAPP=['EDITMODE', db.editmode])

if __name__ == '__main__':
    app.debug = settings.DEBUG
    app.run(host=settings.HTTP_HOST, port=settings.HTTP_PORT)
