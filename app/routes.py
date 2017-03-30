from app import app, mdb
import flask
from config import *


''' API here onwards to be built by Saurabh '''

def connect_database():
    try:
        con = mdb.connect(SQL_DATABASE_URI, SQL_DATABASE_USER, \
                      SQL_DATABASE_PASS, SQL_DATABASE_SCHEMA, \
                      use_unicode=True, charset='utf8')
        return con

    except Exception as e:
        print(e)
        return None


@app.route('/search', methods=['GET'])
def search():
    con = connect_database()
    cursor = con.cursor()
    # Example query
    sql_query = 'SELECT * FROM UserProfile'
    cursor.execute(sql_query)
    result_data = cursor.fetchall()
    cursor.close()
    con.close()

@app.route('/appointment', methods=['GET'])
def read_appointment():
    pass

@app.route('/appointment', methods=['POST'])
def create_appointment():
    pass

@app.route('/appointment', methods=['PUT'])
def update_appointment():
    pass

@app.route('/appointment', methods=['DELETE'])
def delete_appointment():
    pass

@app.route('/login', methods=['POST'])
def user_login():
    pass

@app.route('/user', methods=['GET'])
def read_user():
    pass

@app.route('/user', methods=['POST'])
def create_user():
    pass

@app.route('/user', methods=['PUT'])
def update_user():
    pass

''' API here onwards to be built by Aditya '''

@app.route('/user', methods=['DELETE'])
def delete_user():
    pass

@app.route('/logout', methods=['POST'])
def user_logout():
    pass

@app.route('/review', methods=['GET'])
def read_review():
    pass

@app.route('/review', methods=['POST'])
def create_review():
    pass

@app.route('/review', methods=['PUT'])
def update_review():
    pass

@app.route('/review', methods=['DELETE'])
def delete_review():
    pass

@app.route('/availability', methods=['GET'])
def read_availability():
    pass

@app.route('/availability', methods=['POST'])
def create_availability():
    pass
