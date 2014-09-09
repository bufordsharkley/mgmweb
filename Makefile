# A simple way to update Flask Heroku's static files.

# ----------------------
#  Useful variables
# ----------------------
NORM=\033[0m
BOLD=\033[1m
CHECK=\033[32m✔\033[39m
port=5000

.PHONY: build test server clean clean-all

build:
	virtualenv env
	. env/bin/activate && env/bin/pip install -r requirements.txt

test:
	. env/bin/activate && env/bin/nosetests

server:
	. env/bin/activate && env/bin/python scripts/runweb.py

clean:
	find . -name "*.pyc" -exec rm {} \;

clean-all: clean
	rm -rf env
