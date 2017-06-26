test:
	env/bin/python test.py

freeze:
	env/bin/python freeze.py

server: freeze
	cd mgmweb/build && python -m SimpleHTTPServer
