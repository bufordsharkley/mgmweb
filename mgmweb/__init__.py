import datetime
import os
import random
import re

import flask
import jinja2
import markdown
import yaml

#from .drawing_metadata import metadata
from .film_logic import organize_month_data_into_tiers, flesh_out_rewatches
from .frontpage_descriptions import splash_descriptions
from .film_100 import top100films

app = flask.Flask(__name__)


def get_content(app):
    return yaml.load(app.open_resource('static/radiocontent.yaml'),
                     Loader=yaml.FullLoader)


@app.route('/')
def index():
    return flask.render_template('index.html',
                                 splash=splash_descriptions['default'])


@app.route('/<path:path>/')
def subpage(path):
    try:
        return flask.render_template(path + '.html')
    except jinja2.TemplateNotFound:
        flask.abort(404)


@app.route('/etc/')
def etc():
    poem_dir = os.path.join(app.root_path, 'static/markdown/poems')
    poems = []
    for poem in os.listdir(poem_dir):
        src = app.open_resource(os.path.join(poem_dir, poem), 'r').read()
        link = poem.rsplit('.md', 1)[0]
        yaml_data, src = _extract_md_yaml(src)
        year = yaml_data['year']
        title = yaml_data['title']
        poems.append((title, year, link))
    poems.sort(key=lambda x: x[1], reverse=True)
    return flask.render_template('etc.html', poems=poems)


@app.route('/radio/')
def radio_landing():
    content = get_content(app)
    plays = yaml.load(app.open_resource('static/radioplays.yaml'), Loader=yaml.FullLoader)
    return flask.render_template('radio.html', content=content, plays=plays)


@app.route('/drawing/<int:num>/')
def drawing(num):
    metadata = yaml.load(app.open_resource('static/drawing_metadata.yaml'), Loader=yaml.FullLoader)
    try:
        firstorlast = None
        if num == len(metadata):
            firstorlast = 'last'
        if num == 1:
            firstorlast = 'first'
        metadatum = sorted(metadata, key=lambda k: k['number'])[num-1]
    except IndexError:
        flask.abort(404)
    return flask.render_template('drawing.html',
                           number=metadatum['number'],
                           small_src=metadatum['src_small'],
                           large_src=metadatum['src_large'],
                           date=metadatum['date'],
                           caption=metadatum.get('caption', ''),
                           additionaltext=metadatum.get('wordsinimage', ''),
                           firstorlast = firstorlast)


@app.route('/drawing/')
@app.route('/drawing/random/')
def random_drawing():
    metadata = yaml.load(app.open_resource('static/drawing_metadata.yaml'), Loader=yaml.FullLoader)
    return flask.render_template('randomdrawing.html',
                                 drawcount = len(metadata))


@app.route('/drawing/last/')
def last_drawing():
    metadata = yaml.load(app.open_resource('static/drawing_metadata.yaml'), Loader=yaml.FullLoader)
    return flask.redirect(flask.url_for('drawing', num=len(metadata)))


@app.route('/infomercial/')
@app.route('/superbocooker/')
@app.route('/superbo-cooker/')
@app.route('/superbo_cooker/')
def infomercial():
    return flask.redirect(flask.url_for('drawing', num=2))


@app.route('/writings/')
def all_writings():
    return flask.redirect(flask.url_for('subpage', path='etc'))
    try:
        return flask.render_template('/writings/' + opus + '.html')
    except jinja2.TemplateNotFound:
        flask.abort(404)


@app.route('/writings/<path:opus>/')
def writings(opus):
    try:
        return flask.render_template('/writings/' + opus + '.html')
    except jinja2.TemplateNotFound:
        flask.abort(404)


@app.route('/poems/<opus>/')
def poems(opus):
    try:
        src = app.open_resource('static/markdown/poems/{}.md'.format(opus), 'r')
    except IOError:
        flask.abort(404)
    src = src.read()
    yaml_data, src = _extract_md_yaml(src)
    year = yaml_data['year']
    # replace regular line breaks with two spaces so markdown sees line breaks:
    src = re.sub(r'([^\n])\n', r'\1  \n', src)
    content = markdown.markdown(src)
    title = opus.replace('_', ' ')
    return flask.render_template('poem.html', **locals())


def _extract_md_yaml(text):
    if text.startswith('---'):
        _, yaml_txt, main_md = text.split('---', 2)
        yaml_data = yaml.safe_load(yaml_txt)
        return yaml_data, main_md
    return {}, main_md


@app.route('/bridge.pdf')
def bridge_flowchart():
    return flask.send_from_directory(app.static_folder, 'BRIDGEFLOWCHART.pdf')


@app.route('/robots.txt')
@app.route('/humans.txt')
@app.route('/friends.txt')
@app.route('/hackers.txt')
@app.route('/keybase.txt')
def static_from_root():
    return flask.send_from_directory(app.static_folder, flask.request.path[1:])


@app.route('/<htmlfile>.html/')
def html_call(htmlfile):
    return flask.render_template(htmlfile + '.html')


@app.route('/_frontpagedescriptions.json')
def frontpagedescriptions():
    return flask.jsonify(splash_descriptions)


@app.route('/404.html')
def intentional_404():
    return flask.render_template('error.html')


@app.errorhandler(404)
def page_not_found(e):
    return flask.render_template('error.html'), 404


@app.errorhandler(500)
@app.route('/500/', defaults={'e': 'e'})
def page_error(e):
    return flask.render_template('error.html'), 200


@app.route('/film100/')
def film100():
    return flask.render_template('film100.html', films=top100films)


@app.route('/film/')
def film():
    films = yaml.load(app.open_resource('static/master.yaml'),
                      Loader=yaml.FullLoader)
    random.shuffle(films[-1]['films'])
    return flask.render_template('film.html', films=films)

#@app.route('/films/')
#<meta http-equiv="Refresh" content="0; url='https://your.redirect.here'" />


@app.route('/film/ranked.html')
def film_ranked():
    films = yaml.load(app.open_resource('static/master.yaml'),
                      Loader=yaml.FullLoader)
    films = flesh_out_rewatches(films)
    months = [(x['month'], organize_month_data_into_tiers(x)) for x in films
              if x['status'] == 'ranked']
    return flask.render_template('film_ranked.html', months=months)


@app.route('/garfield/')
def garfield_mirror():
    return flask.render_template('garfield.html')


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
    return flask.render_template('heartdemo.html')


if __name__ == '__main__':
    application.run(debug=True)
