import datetime
import random

from flask import Flask, render_template, abort, redirect, url_for
from jinja2 import TemplateNotFound

from .drawing_metadata import metadata

application = app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/<path:path>/')
def subpage(path):
    try:
        return render_template(path + '.html')
    except TemplateNotFound:
        abort(404)


@app.route('/drawing/<int:num>/')
def drawing(num):
    try:
        metadatum = sorted(metadata, key=lambda k: k['number'])[num-1]
    except IndexError:
        abort(404)
    return render_template('drawing.html',
                           number=metadatum['number'],
                           small_src=metadatum['image']['src_small'],
                           date=metadatum['date'],
                           caption=metadatum.get('caption',''),
                           additionaltext=metadatum.get('wordsinimage',''))


@app.route('/drawing/')
@app.route('/drawing/random/')
def random_drawing():
    metadatum = metadata[random.randrange(len(metadata)) + 1]
    return redirect(url_for('drawing', num=random.randrange(len(metadata))))


@app.route('/hackers.txt')
def hackers():
    return 'site has been hacked at time: {}'.format(datetime.datetime.now())


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    application.run(debug=True)
