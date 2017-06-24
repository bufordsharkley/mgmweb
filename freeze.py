import flask_frozen

import app

freezer = flask_frozen.Freezer(app.app)


#@freezer.register_generator
#def episode():
    #for ep in app.get_eps():
        #yield {'date': ep}


@freezer.register_generator
def error_handlers():
    yield "/404"

freezer.freeze()
