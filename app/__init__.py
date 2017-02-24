from flask import Flask
import MySQLdb as mdb
from config import *


app = Flask(__name__)
app.config.from_object('config')

con = mdb.connect(SQL_DATABASE_URI, SQL_DATABASE_USER, \
                  SQL_DATABASE_PASS, SQL_DATABASE_SCHEMA)

from app import views

