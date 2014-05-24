import os
import subprocess

from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
from linkmanager import settings
from linkmanager.db import DataBase

app = Flask(__name__)


def launch_browser(BROWSER=False):
    subprocess.Popen(
        'sleep 0.5;nohup %s http://127.0.0.1:%s/ &' % (
            BROWSER,
            settings.HTTP_PORT
        ),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        shell=True
    )


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/search", methods=['POST'])
def search():
    try:
        tags = next(request.form.items())[0].split()
    except:
        return jsonify({})
    results = {}
    db = DataBase()
    links = db.sorted_links(*tags)
    results = {}
    for l in links:
        properties = db.get_link_properties(l)
        results[l] = properties

    return jsonify(**results)


@app.route("/suggest")
def suggest():
    keywords = request.args.get('tags').split()
    last_keyword = keywords[len(keywords) - 1]
    str_suggestion = ' '.join(keywords[:-1])
    d = DataBase()

    suggestions = {}
    for s in d.complete_tags(last_keyword):
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
    app.run(port=settings.HTTP_PORT)
