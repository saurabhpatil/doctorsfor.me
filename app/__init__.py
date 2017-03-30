from flask import Flask
import MySQLdb as mdb


app = Flask(__name__)
app.config.from_object('config')

from app import routes

