#build:
	#virtualenv env
	#. env/bin/activate && env/bin/pip install -r requirements.txt
#
#test:
	#. env/bin/activate && env/bin/nosetests
#
#server:
	#. env/bin/activate && env/bin/python app.py
#
#clean:
	#find . -name "*.pyc" -exec rm {} \;
#
#clean-all: clean
	#rm -rf env

freeze:
	env/bin/python freeze.py

server: freeze
	python -m SimpleHTTPServer
