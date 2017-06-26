import os

from mgmweb import app

# Some notes from http://stevenloria.com/hosting-static-flask-sites-for-free-on-github-pages/
APP_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR))
# In order to deploy to Github pages, you must build the static files to
# the project root
app.config['FREEZER_DESTINATION'] = PROJECT_ROOT
app.config['FREEZER_BASE_URL'] = "http://localhost/"
app.config['FREEZER_REMOVE_EXTRA_FILES'] = False  # IMPORTANT: If this is True, all app files
                                    # will be deleted when you run the freezer


if __name__ == '__main__':
    app.run(debug=True)
