test:
	uv run test.py

freeze:
	uv run freeze.py

server: freeze
	cd mgmweb/build && python -m http.server
