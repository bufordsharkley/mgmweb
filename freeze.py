import datetime

import flask_frozen
import requests

import mgmweb
import app

freezer = flask_frozen.Freezer(app.app)


def check_url_validity(content):
    for content_type, content_content in content.items():
        print(content_type)
        for morsel in content_content:
            url = morsel['url']
            if content_type == 'loon':
                date_check = datetime.datetime.strptime(
                        url.rsplit('/', 1)[1].split('.')[0], '%Y-%m-%d')
                assert date_check.date() == morsel['datetime'].date()
            # TODO: check datetime, other info against overall list of show data
            print(url)
            r = requests.head(url)
            r.raise_for_status()
            try:
                yaml_size = int(morsel['audio size'])
                head_size = int(r.headers['Content-Length'])
                if yaml_size != head_size:
                    print('Discrepancy: {} vs {}'.format(yaml_size, head_size))
            except KeyError:
                # No need, who cares
                pass


@freezer.register_generator
def error_handlers():
    yield "/404/"


@freezer.register_generator
def break_handlers():
    yield "/500/"


@freezer.register_generator
def real_error_handlers():
    yield "/error/"


@freezer.register_generator
def frontpageajax():
   yield "/_frontpagedescriptions.json"


@freezer.register_generator
def cv_why_not():
   yield "/cv.html"


@freezer.register_generator
def film_ranked():
   yield "/film/ranked.html"

@freezer.register_generator
def robots_and_humans_and_friends_and_hackers():
    for cool_page in ('robots', 'humans', 'friends', 'hackers'):
        yield "/{}.txt".format(cool_page)


def main():
    content = mgmweb.get_content(app.app)
    check_url_validity(content)
    freezer.freeze()

if __name__ == "__main__":
    main()
