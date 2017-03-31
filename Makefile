.PHONY: install test

install:
		pip install -qr requirements.txt

test:
		nosetests -sv app/test.py

run:
		python server.py

prod-run:
		gunicorn application:app --worker-class=gevent

		

