# doctorsforme-backend

Web app for DoctorsFor.me

## User Stories
- [ ] User can signup for the service and use it. [Saurabh]
- [x] User can log in to their account and then logout. [Aditya]

## Setup

- Dev server: `python server.py`
- Prod server: `gunicorn application:app --worker-class=gevent`
- Configuration: `config.py` to store variables
- Procfile: Heroku web deployment file
- Makefile: Easy access to frequently used commands
- Dependencies: `requirements.txt` for python packages used

## Install

1. Install virtualenv: `pip install virtualenv`
2. Create virtual environment: `virtualenv venv`
3. Install dependecies: `pip install -qr requirements.txt`
4. Set environment variable: SQL_DATABASE_URI to URL of MySQL server
4. Run dev: `make run` or prod: `make prod-run`
