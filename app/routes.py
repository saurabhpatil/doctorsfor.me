from app import app, mdb
from flask import request, json
from config import *
import os


''' API here onwards to be built by Saurabh '''

def connect_database():
    try:
        con = mdb.connect(os.environ.get('SQL_DATABASE_URI'), SQL_DATABASE_USER, \
                      SQL_DATABASE_PASS, SQL_DATABASE_SCHEMA, \
                      use_unicode=True, charset='utf8')
        return con
    except Exception as e:
        print(e)
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    return '<h1>Howdy, Ags!</h1><h3>API server is running normally. Refer to API doc on Google Drive for usage.</h3>'

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
    return 'Hello World'

@app.route('/appointment', methods=['GET'])
def read_appointment():
    pass

@app.route('/appointment', methods=['POST'])
def create_appointment():
    # Refer this: http://flask.pocoo.org/docs/0.12/quickstart/#accessing-request-data
    pass

@app.route('/appointment', methods=['PUT'])
def update_appointment():
    pass

@app.route('/appointment', methods=['DELETE'])
def delete_appointment():
    pass

@app.route('/login', methods=['POST'])
def user_login():
     # Refer this: http://flask.pocoo.org/docs/0.12/quickstart/#accessing-request-data
    pass

@app.route('/user', methods=['GET'])
def read_user():
    pass

@app.route('/user', methods=['POST'])
def create_user():
     # Refer this: http://flask.pocoo.org/docs/0.12/quickstart/#accessing-request-data
    pass

@app.route('/user', methods=['PUT'])
def update_user():
    pass

''' API here onwards to be built by Aditya '''

@app.route('/user/patient/<int:id>', methods=['DELETE'])
def delete_patient(id):

    result = dict()
    result['success'] = False
    profile_id = id

    try:
        # Connect to database
        con = connect_database()
        cursor = con.cursor()

        # Get id from customer table
        sql_query = 'SELECT customer_id FROM customer WHERE profile_id={}'.format(profile_id)
        cursor.execute(sql_query)
        customer_id = cursor.fetchone()
        customer_id = int(customer_id[0])

        # Delete all appointments for patient
        sql_query = 'DELETE FROM appointment WHERE customer_id={}'.format(customer_id)
        cursor.execute(sql_query)

        # Delete from customer table
        sql_query = 'DELETE FROM customer WHERE profile_id={}'.format(profile_id)
        cursor.execute(sql_query)

        # Delete from user_profile table
        sql_query = 'DELETE FROM user_profile WHERE profile_id={}'.format(profile_id)
        cursor.execute(sql_query)
       
        # Close connections
        cursor.close()
        con.commit()
        result['success'] = True
        return json.dumps(result)

    except Exception as e:
        con.rollback()
        return json.dumps(result)
    finally:
        con.close()

@app.route('/user/doctor/<int:id>', methods=['DELETE'])
def delete_doctor(id):

    result = dict()
    result['success'] = False
    profile_id = id

    try:
        # Connect to database
        con = connect_database()
        cursor = con.cursor()

        # Get id from customer table
        sql_query = 'SELECT doctor_id FROM doctor WHERE profile_id={}'.format(profile_id)
        cursor.execute(sql_query)
        doctor_id = cursor.fetchone()
        doctor_id = int(doctor_id[0])

        # Delete all appointments for patient
        sql_query = 'DELETE FROM appointment WHERE doctor_id={}'.format(doctor_id)
        print(sql_query)
        cursor.execute(sql_query)

        # Delete from customer table
        sql_query = 'DELETE FROM doctor WHERE profile_id={}'.format(profile_id)
        print(sql_query)
        cursor.execute(sql_query)

        # Delete from user_profile table
        sql_query = 'DELETE FROM user_profile WHERE profile_id={}'.format(profile_id)
        print(sql_query)
        cursor.execute(sql_query)
       
        # Close connections
        cursor.close()
        con.commit()
        result['success'] = True
        return json.dumps(result)

    except Exception as e:
        con.rollback()
        result['error'] = e 
        return json.dumps(result)
    finally:
        con.close()


@app.route('/logout/<user_type>/<int:id>', methods=['POST'])
def user_logout(user_type, id):
    result = dict()
    result['success'] = True
    return json.dumps(result)

@app.route('/review', methods=['GET'])
def read_review():
    result = dict()
    result['success'] = False

    profile_id = request.args.get('id', None)
    user_type = request.args.get('user_type', None)

    # Check for null data
    if profile_id is None or user_type is None:
        result['error'] = 'Either profile_id or user_type is null.'
        return result
    elif user_type != 'doctor':
        result['error'] = 'Request should contain doctor as user_type.'
        return result

    try:
        # Connect to database
        con = connect_database()
        cursor = con.cursor()

        # Get doctor_id from doctor table
        sql_query = 'SELECT doctor_id FROM doctor WHERE profile_id={}'.format(profile_id)
        cursor.execute(sql_query)
        doctor_id = cursor.fetchone()
        doctor_id = int(doctor_id[0])

        # Get list of reviews from reviews table
        sql_query = "SELECT R.review_id, R.score, R.comment, U.full_name \
                     FROM reviews as R \
                     INNER JOIN customer as C ON R.customer_id=C.customer_id \
                     INNER JOIN user_profile as U ON C.profile_id=U.profile_id \
                     WHERE R.doctor_id={}".format(doctor_id)
        cursor.execute(sql_query)
        reviews_iterator = cursor.fetchall()

        result['reviews'] = list()

        # Return list of reviews
        for review in reviews_iterator:
            review_dict = dict()
            review_dict['review_id'] = int(review[0])
            review_dict['score'] = int(review[1])
            review_dict['comment'] = unicode(review[2])
            review_dict['full_name'] = unicode(review[3])
            result['reviews'].append(review_dict)
        
        # Close connections
        cursor.close()
        con.commit()
        result['success'] = True
        return json.dumps(result)

    except Exception as e:
        con.rollback()
        result['error'] = str(e)
        return json.dumps(result)
    finally:
        con.close()

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
