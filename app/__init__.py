from flask import Flask
import MySQLdb as mdb
from flask_cors import CORS


app = Flask(__name__)
app.config.from_object('config')
CORS(app)

from app import routes

