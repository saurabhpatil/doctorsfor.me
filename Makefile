.PHONY: install test

install:
		pip install -qr requirements.txt

test:
		nosetests test

run:
		python server.py

prod-run:
		gunicorn application:app --worker-class=gevent

		

