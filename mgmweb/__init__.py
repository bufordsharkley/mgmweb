import datetime
import os

from flask import Flask, render_template, abort, redirect, url_for, jsonify,\
    send_from_directory, request, Markup
from jinja2 import TemplateNotFound
import markdown2

from .drawing_metadata import metadata
from .frontpage_descriptions import splash_descriptions
from .film_100 import top100films

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html', splash=splash_descriptions['default'])


@app.route('/<path:path>/')
def subpage(path):
    try:
        return render_template(path + '.html')
    except TemplateNotFound:
        abort(404)


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
        abort(404)
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
    return redirect(url_for('drawing', num=len(metadata)))


@app.route('/infomercial/')
@app.route('/superbocooker/')
@app.route('/superbo-cooker/')
@app.route('/superbo_cooker/')
def infomercial():
    return redirect(url_for('drawing', num=2))


@app.route('/writings/', defaults={'opus':''})
@app.route('/writings/<path:opus>/')
def writings(opus):
    if not opus:
        return render_template('/etc.html')
    try:
        return render_template('/writings/' + opus + '.html')
    except TemplateNotFound:
        abort(404)


@app.route('/markdownwriting/<title>/')
def writing_with_markdown(title):
    filepath = os.path.join(app.static_folder, 'writings',
                            '{}.md'.format(title))
    try:
        with open(filepath) as f:
            content = f.read()
    except IOError:
        abort(404)
    content = Markup(markdown2.markdown(content, extras=["smarty-pants"]))
    return render_template('/poem.html', content=content)


@app.route('/bridge/')
def bridge_flowchart():
    return send_from_directory(app.static_folder, 'BRIDGEFLOWCHART.pdf')


@app.route('/robots.txt')
@app.route('/humans.txt')
@app.route('/hackers.txt')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])


@app.route('/<htmlfile>.html/')
def html_call(htmlfile):
    return render_template(htmlfile + '.html')


@app.route('/_frontpagedescriptions/', defaults={'button': ''})
@app.route('/_frontpagedescriptions/<button>/')
def frontpagedescriptions(button):
    if not button:
        return jsonify(splash_descriptions)
    try:
        return jsonify(splash_descriptions[button])
    except KeyError:
        return jsonify(splash_descriptions['default'])


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/film100/')
def film100():
    return render_template('film100.html', films=top100films)

# as of yet un-documented routes:
@app.route('/heartdemo/')
def heartdemo():
    return render_template('heartdemo.html')


if __name__ == '__main__':
    application.run(debug=True)
