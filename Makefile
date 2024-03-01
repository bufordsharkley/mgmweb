test:
	env/bin/python test.py

freeze:
	python freeze.py

server: freeze
	cd mgmweb/build && python -m http.server
