# A simple way to update Flask Heroku's static files.

.PHONY: build test server clean clean-all

build:
	virtualenv env
	. env/bin/activate && env/bin/pip install -r requirements.txt

test:
	. env/bin/activate && env/bin/nosetests

server:
	. env/bin/activate && env/bin/python app.py

clean:
	find . -name "*.pyc" -exec rm {} \;

clean-all: clean
	rm -rf env
