# doctorsforme-backend

Web app for DoctorsFor.me

## User Stories
- [ ] Client can search for doctors in an area. 
- [ ] Client can create, read, update and delete appointments.
- [ ] Client can login a user.
- [ ] Client can logout a user.
- [ ] Client can create, read, update and delete user accounts.
- [ ] Client can create, read, update and delete reviews.
- [ ] Client can read and create slots for doctor's availability.

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
4. Set environment variable: `SQL_DATABASE_URI` to have value as URL of MySQL server
4. Run dev: `make run` or prod: `make prod-run`
