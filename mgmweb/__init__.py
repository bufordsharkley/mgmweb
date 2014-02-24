from flask import Flask, render_template, abort
from jinja2 import TemplateNotFound

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

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    application.run(debug=True)
