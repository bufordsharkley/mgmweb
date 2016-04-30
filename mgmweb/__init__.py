import datetime
import random

import flask
from flask import render_template, request
from jinja2 import TemplateNotFound
import markdown

from .drawing_metadata import metadata
from .frontpage_descriptions import splash_descriptions
from .film_100 import top100films

app = flask.Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html', splash=splash_descriptions['default'])


@app.route('/<path:path>/')
def subpage(path):
    try:
        return render_template(path + '.html')
    except TemplateNotFound:
        flask.abort(404)


@app.route('/drawing/<int:num>/')
def drawing(num):
    try:
        firstorlast = None
        if num == len(metadata):
            firstorlast = 'last'
        if num == 1:
            firstorlast = 'first'
        metadatum = sorted(metadata, key=lambda k: k['number'])[num-1]
    except IndexError:
        flask.abort(404)
    return render_template('drawing.html',
                           number=metadatum['number'],
                           small_src=metadatum['image']['src_small'],
                           large_src=metadatum['image']['src_large'],
                           date=metadatum['date'],
                           caption=metadatum.get('caption', ''),
                           additionaltext=metadatum.get('wordsinimage', ''),
                           firstorlast = firstorlast)


@app.route('/drawing/')
@app.route('/drawing/random/')
def random_drawing():
    return render_template('randomdrawing.html', drawcount = len(metadata))


@app.route('/drawing/last/')
def last_drawing():
    return flask.redirect(flask.url_for('drawing', num=len(metadata)))


@app.route('/infomercial/')
@app.route('/superbocooker/')
@app.route('/superbo-cooker/')
@app.route('/superbo_cooker/')
def infomercial():
    return flask.redirect(flask.url_for('drawing', num=2))


@app.route('/writings/', defaults={'opus':''})
@app.route('/writings/<path:opus>/')
def writings(opus):
    if not opus:
        return render_template('/etc.html')
    try:
        return render_template('/writings/' + opus + '.html')
    except TemplateNotFound:
        flask.abort(404)


@app.route('/bridge/')
def bridge_flowchart():
    return flask.send_from_directory(app.static_folder, 'BRIDGEFLOWCHART.pdf')


@app.route('/robots.txt')
@app.route('/humans.txt')
@app.route('/friends.txt')
@app.route('/hackers.txt')
@app.route('/keybase.txt')
def static_from_root():
    return flask.send_from_directory(app.static_folder, request.path[1:])


@app.route('/<htmlfile>.html/')
def html_call(htmlfile):
    return render_template(htmlfile + '.html')


@app.route('/_frontpagedescriptions/', defaults={'button': ''})
@app.route('/_frontpagedescriptions/<button>/')
def frontpagedescriptions(button):
    if not button:
        return flask.jsonify(splash_descriptions)
    try:
        return flask.jsonify(splash_descriptions[button])
    except KeyError:
        return flask.jsonify(splash_descriptions['default'])


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404


@app.errorhandler(500)
@app.route('/500/', defaults={'e': 'e'})
def page_error(e):
    return render_template('error.html'), 404


@app.route('/film100/')
def film100():
    return render_template('film100.html', films=top100films)


@app.route('/garfield/')
def garfield_mirror():
    return render_template('garfield.html')


@app.route('/mediumish/<post>')
def mediumish(post):
    source = app.open_resource('static/markdown/{}.md'.format(post)).read()
    source = unicode(source, 'utf-8')
    content = flask.Markup(markdown.markdown(source))
    title = post.replace('_', ' ')
    return flask.render_template('mediumish.html', **locals())


# as of yet un-documented routes:
@app.route('/heartdemo/')
def heartdemo():
    return render_template('heartdemo.html')


if __name__ == '__main__':
    application.run(debug=True)
