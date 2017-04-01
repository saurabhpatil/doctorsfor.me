from app import app, mdb
from flask import request, json
from config import *
import os
import datetime, time

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

''' API here onwards to be built by Saurabh '''

@app.route('/search', methods=['GET'])
def search():
    result = dict()
    result['success'] = False

    city = request.args.get('city', None)
    doctor_type = request.args.get('type', None)

    # Check for null data
    if city is None and doctor_type is None:
        result['error'] = 'Either profile_id or user_type is null.'
        return result

    try:
        # Connect to database
        con = connect_database()
        cursor = con.cursor()

        # Get search results from doctor, user_profile and review tables
        sql_query = '''select d.doctor_id, u.photo_url, u.full_name, d.qualification, d.experience, d.type,
                              d.address, avg(r.score)
                        from reviews r doctor_id
                        inner join doctor d on d.doctor_id = r.doctor_id
                        inner join user_profile u on d.profile_id = u.profile_id
                        where d.type = {} or u.city = {}
                        group by d.doctor_id, u.full_name, d.experience, d.type, d.qualification, d.address, u.photo_url''' \
            .format(type, city)
        cursor.execute(sql_query)
        search_iterator = cursor.fetchall()
        result['search'] = list()

        # Return list of reviews
        for search_result in search_iterator:
            search_dict = dict()
            search_dict['doctor_id'] = int(search_result[0])
            search_dict['photo_url'] = unicode(search_result[1])
            search_dict['name'] = unicode(search_result[2])
            search_dict['qualification'] = unicode(search_result[3])
            search_dict['experience'] = int(search_result[4])
            search_dict['address'] = unicode(search_result[6])
            search_dict['rating'] = float(search_result[7])
            result['search'].append(search_dict)

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

@app.route('/appointment', methods=['GET'])
def read_appointment():
    result = dict()
    result['success'] = False

    profile_id = request.args.get('id', None)
    user_type = request.args.get('user_type', None)

    # Check for null data
    if profile_id is None or user_type is None:
        result['error'] = 'Either profile_id or user_type is null.'
        return result

    try:
        # Connect to database
        con = connect_database()
        cursor = con.cursor()

        # Get appointments for doctor or customer
        if user_type == 'doctor':
            sql_query = '''select a.appointment_id, u.full_name, a.date, a.time, u.phone
                            from appointment a, user_profile u
                            where a.doctor_id = {} and u.profile_id = a.customer_id'''.format(profile_id)
        else:
            sql_query = '''select a.appointment_id, u.full_name, a.date, a.time, d.address, u.phone
                            from appointment a, user_profile u, doctor d
                            where a.customer_id = {} and u.profile_id = a.doctor_id
                            and d.profile_id = u.profile_id'''.format(profile_id)

        cursor.execute(sql_query)
        appointment_iterator = cursor.fetchall()
        result['appointments'] = list()

        # Return list of reviews
        for appointment in appointment_iterator:
            appointment_dict = dict()
            appointment_dict['appointment_id'] = int(appointment[0])
            appointment_dict['name'] = unicode(appointment[1])
            appointment_dict['date'] = unicode(appointment[2])
            appointment_dict['time'] = unicode(appointment[3])
            appointment_dict['address'] = unicode(appointment[4]) if user_type == 'patient' else None
            appointment_dict['phone'] = unicode(appointment[0])
            result['appointments'].append(search_dict)

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

@app.route('/appointment', methods=['POST'])
def create_appointment():
    result = dict()
    result['success'] = False

    customer_id = request.form.get('customer_id')
    doctor_id = request.form.get('doctor_id')
    date = request.form.get('date')
    time = request.form.get('time')

    # Check for null data
    if doctor_id is None or customer_id is None:
        result['error'] = 'Either doctor_id or customer_id is null.'
        return result
    elif date is None or time is None:
        result['error'] = 'Both date and time are required. check the parameters'
        return result

    try:
        # Connect to database
        con = connect_database()
        cursor = con.cursor()

        # check if user exists
        sql_query = 'INSERT INTO appointment(customer_id, doctor_id, date, time) VALUES ({}, {}, {}, {})'\
                    .format(customer_id, doctor_id, date, time)
        cursor.execute(sql_query)

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

@app.route('/appointment', methods=['PUT'])
def update_appointment():
    pass

@app.route('/appointment/<int:id>', methods=['DELETE'])
def delete_appointment(id):
    result = dict()
    result['success'] = False
    appointment_id = id

    try:
        # Connect to database
        con = connect_database()
        cursor = con.cursor()

        # Get id from customer table
        sql_query = 'DELETE FROM appointment WHERE appointment_id = {}'.format(appointment_id)
        cursor.execute(sql_query)
        cursor.close()
        con.commit()
        result['success'] = True
        return json.dumps(result)

    except Exception as e:
        con.rollback()
        return json.dumps(result)
    finally:
        con.close()

@app.route('/login', methods=['POST'])
def user_login():
    result = dict()
    result['success'] = False

    username = request.form.get('username')
    password = request.form.get('password')

    # Check for null data
    if username is None:
        result['error'] = 'username is null'
        return result
    elif password is None:
        result['error'] = 'password is null'
        return result

    try:
        con = connect_database()
        cursor = con.cursor()

        # Get id from customer table
        sql_query = 'SELECT 1 FROM user_profile WHERE username={} and password = {}'.format(username, password)
        cursor.execute(sql_query)
        login_success = cursor.fetchone()

        if login_success is None:
            return json.dumps(result)

        result['success'] = True
        return json.dumps(result)

    except Exception as e:
        con.rollback()
        return json.dumps(result)
    finally:
        con.close()

@app.route('/user', methods=['GET'])
def read_user():
    result = dict()
    result['success'] = False

    id = request.args.get('id', None)
    user_type = request.args.get('user_type', None)

    # Check for null data
    if id is None or user_type is None:
        result['error'] = 'Either id or user_type is null.'
        return result

    try:
        # Connect to database
        con = connect_database()
        cursor = con.cursor()

        # get doctor or customer info
        if user_type == 'doctor':
            sql_query = '''SELECT u.full_name, u.city, u.state, u.country, u.phone, u.email, u.photo_url,
                                  d.address, d.experience, d.qualification
                          FROM doctor d, user_profile u
                          WHERE d.profile_id = u.profile_id AND d.doctor_id = {}'''\
                        .format(int(id))
        else:
            sql_query = '''SELECT u.full_name, u.city, u.state, u.country, u.phone, u.email, u.photo_url
                            FROM customer c, user_profile u
                            WHERE c.profile_id = u.profile_id AND c.customer_id = {}'''\
                        .format(int(id))
        cursor.execute(sql_query)
        info = cursor.fetchone()
        info_dict = dict()
        info_dict['name'] = unicode(info[0])
        info_dict['city'] = unicode(info[1])
        info_dict['state'] = unicode(info(2))
        info_dict['country'] = unicode(info(3))
        info_dict['phone'] = unicode(info(4))
        info_dict['email'] = unicode(info(5))
        info_dict['photo_url'] = unicode(info(6))

        if user_type == 'doctor':
            info_dict['address'] = unicode(info(7))
            info_dict['experience'] = int(info(8))
            info_dict['qualification'] = unicode(info(9))

        result['info'] = info_dict

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

@app.route('/user', methods=['POST'])
def create_user():
    result = dict()
    result['success'] = False

    full_name = request.form.get('name')
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')
    phone = request.form.get('phone')
    address = request.form.get('address')
    city = request.form.get('city')
    state = request.form.get('state')
    country = request.form.get('country')
    user_type = request.form.get('user_type')

    # Check for null data
    if username is None or password is None or email is None:
        result['error'] = 'Either username, password or email is null.'
        return result
    elif user_type is None:
        result['error'] = 'User_Type is required'
        return result

    try:
        # Connect to database
        con = connect_database()
        cursor = con.cursor()

        # check if user exists
        sql_query = 'SELECT 1 FROM user_profile WHERE username={} or email = {}'.format(username, email)
        cursor.execute(sql_query)
        existing_user = cursor.fetchone()
        if existing_user is not None:
            result['error'] = 'User already exists'
            return json.dumps(result)

        # add record to user_profile
        sql_query = "INSERT INTO user_profile(username, password, email, phone, full_name, state, city, country) " \
                    "VALUES('{}','{}','{}','{}','{}','{}','{}','{}');"\
                    "SET @PROFILE_ID = LAST_INSERT_ID();"\
                    "IF '{}' = 'doctor' THEN " \
                    "INSERT INTO doctor(profile_id, location, address) VALUES(@PROFILE_ID,'{}','{}');" \
                    "ELSE InSERT INTO customer(profile_id) VALUES(@PROFILE_ID);" \
                    "END IF;"\
                    .format(username, password, email, phone, full_name, state, city, country, user_type, city, address)
        print(sql_query)
        cursor.execute(sql_query)

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
    result = dict()
    result['success'] = False

    profile_id = request.form.get('id')
    user_type = request.form.get('user_type')
    doctor_id = request.form.get('doctor_id')
    score = request.form.get('score')
    comment = request.form.get('comment')
    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

    # Check for null data
    if profile_id is None or user_type is None:
        result['error'] = 'Either profile_id or user_type is null.'
        return result
    elif user_type != 'patient':
        result['error'] = 'Request should contain patient as user_type.'
        return result

    try:
        # Connect to database
        con = connect_database()
        cursor = con.cursor()

        # Get customer_id from customer table
        sql_query = 'SELECT customer_id FROM customer WHERE profile_id={}'.format(profile_id)
        print(sql_query)
        cursor.execute(sql_query)
        customer_id = cursor.fetchone()
        customer_id = int(customer_id[0])

        # # Insert review in reviews table
        sql_query = "INSERT INTO reviews(score, comment, customer_id, doctor_id, date) VALUES({},'{}',{},{},'{}')".format(score, comment, customer_id, doctor_id, timestamp)
        print(sql_query)
        cursor.execute(sql_query)
        
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

@app.route('/review', methods=['PUT'])
def update_review():
    pass

@app.route('/review', methods=['DELETE'])
def delete_review():
    pass

@app.route('/availability', methods=['GET'])
def read_availability():
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
        sql_query = "SELECT date, time FROM availability WHERE doctor_id={}".format(doctor_id)
        cursor.execute(sql_query)
        availability_iterator = cursor.fetchall()

        result['available_slots'] = list()

        # Return list of reviews
        for slot in availability_iterator:
            available_slot = dict()
            available_slot['date'] = slot[0]
            available_slot['time'] = slot[1]
           
            result['available_slots'].append(available_slot)
        
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

@app.route('/availability', methods=['POST'])
def create_availability():
    pass
