import flask_frozen

import app

freezer = flask_frozen.Freezer(app.app)


#@freezer.register_generator
#def episode():
    #for ep in app.get_eps():
        #yield {'date': ep}


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
def robots_and_humans_and_friends_and_hackers():
    for cool_page in ('robots', 'humans', 'friends', 'hackers'):
        yield "/{}.txt".format(cool_page)


freezer.freeze()
