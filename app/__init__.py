from flask import Flask
import MySQLdb as mdb
from flask_cors import CORS

# Create a flask app and configure it
app = Flask(__name__)
app.config.from_object('config')
# Enable CORS 
CORS(app)

from app import routes

