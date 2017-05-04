from app import app, mdb
from flask import request, json
from config import *
import os
import datetime, time


def connect_database():
    """Returns a connection to database"""
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
    '''Returns home page of API server'''
    return '<h1>Howdy, Ags!</h1><h3>API server is running normally. Refer to API doc on Google Drive for usage.</h3>'

@app.route('/search', methods=['GET'])
def search():
    '''Returns search results of doctors for given query'''
    result = dict()
    result['success'] = False

    city = request.args.get('city', None)
    doctor_type = request.args.get('type', None)

    # Check for null data
    if city is None or doctor_type is None:
        result['error'] = 'Either profile_id or user_type is null.'
        return json.dumps(result)

    try:
        # Connect to database
        con = connect_database()
        cursor = con.cursor()

        # Get search results based on doctor type and city
        sql_query = '''select D.profile_id, U.photo_url, U.full_name, D.qualification, D.experience, D.type,
                              D.address, U.city, U.state, U.country,
                              CASE WHEN AVG(R.score) IS NULL THEN 5
                              ELSE AVG(R.score) END
                            FROM user_profile AS U
                            INNER JOIN doctor AS D ON U.profile_id=D.profile_id
                            LEFT OUTER JOIN reviews AS R ON D.doctor_id=R.doctor_id
                            WHERE D.type='{}' AND U.city='{}'
                            GROUP BY D.doctor_id''' \
            .format(doctor_type, city)

        cursor.execute(sql_query)
        search_iterator = cursor.fetchall()
        result['search'] = list()

        # construct a json for all for the search result-set
        for search_result in search_iterator:
            search_dict = dict()
            search_dict['doctor_id'] = int(search_result[0])
            search_dict['photo_url'] = str(search_result[1])
            search_dict['name'] = str(search_result[2])
            search_dict['qualification'] = str(search_result[3])
            search_dict['experience'] = int(search_result[4])
            search_dict['type'] = str(search_result[5])
            search_dict['address'] = str(search_result[6]) + ', ' + str(search_result[7]) + ', ' + str(search_result[8])\
                                     + ', ' + str(search_result[9])
            search_dict['rating'] = int(round(float(search_result[10])))
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
    '''Returns a list of appointments booked by a customer'''
    result = dict()
    result['success'] = False

    profile_id = request.args.get('id', None)
    user_type = request.args.get('user_type', None)

    # Check for null data
    if profile_id is None or user_type is None:
        result['error'] = 'Either profile_id or user_type is null.'
        return json.dumps(result)

    try:
        # Connect to database
        con = connect_database()
        cursor = con.cursor()

        # Get appointments for doctor or customer
        if user_type == 'doctor':
            sql_query = '''select a.appointment_id, c.profile_id, u.full_name, a.date, a.time, u.phone
                            from appointment a, user_profile u, doctor d, customer c
                            where d.profile_id = {}
                            and a.doctor_id = d.doctor_id
                            and a.customer_id = c.customer_id
                            and u.profile_id = c.profile_id'''.format(profile_id)
        else:
            sql_query = '''select a.appointment_id, d.profile_id, u.full_name, a.date, a.time, u.phone, d.address
                            from appointment a, user_profile u, doctor d, customer c
                            where c.profile_id = {}
                            and a.customer_id = c.customer_id
                            and d.doctor_id = a.doctor_id
                            and u.profile_id = d.profile_id'''.format(profile_id)

        cursor.execute(sql_query)
        appointment_iterator = cursor.fetchall()
        result['appointments'] = list()

        # Return list of reviews
        for appointment in appointment_iterator:
            appointment_dict = dict()
            appointment_dict['appointment_id'] = int(appointment[0])
            appointment_dict['name'] = str(appointment[2])
            appointment_dict['date'] = str(appointment[3])
            appointment_dict['time'] = str(appointment[4])
            appointment_dict['phone'] = str(appointment[5])
            if user_type == 'patient':
                appointment_dict['doctor_id'] = str(appointment[1])
                appointment_dict['address'] = str(appointment[6])
            else:
                appointment_dict['customer_id'] = str(appointment[1])
            result['appointments'].append(appointment_dict)

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

@app.route('/appointment', methods=['POST'])
def create_appointment():
    '''Creates a new appointment for given time and date'''
    result = dict()
    result['success'] = False

    customer_id = request.form.get('customer_id')
    doctor_id = request.form.get('doctor_id')
    date = request.form.get('date')
    time = request.form.get('time')

    # Check for null data
    if doctor_id is None or customer_id is None:
        result['error'] = 'Either doctor_id or customer_id is null.'
        return json.dumps(result)
    elif date is None or time is None:
        result['error'] = 'Both date and time are required. check the parameters'
        return json.dumps(result)

    try:
        # Connect to database
        con = connect_database()
        cursor = con.cursor()

        # Insert a new appointment in table, if appointment doesnt exist for the doctor for that date-time combination
        sql_query = '''INSERT IGNORE INTO appointment(customer_id, doctor_id, date, time)
                        SELECT c.customer_id, d.doctor_id, '{}', '{}'
                        FROM customer c, doctor d
                        WHERE c.profile_id = {} AND d.profile_id = {}'''\
                    .format(date, time, customer_id, doctor_id)
        cursor.execute(sql_query)

        # delete the corresponding availability for the doctor
        sql_query = '''DELETE FROM availability
                        WHERE date = '{}' AND time = '{}'
                        AND doctor_id = (SELECT doctor_id FROM doctor WHERE profile_id = {})'''.\
                        format(date, time, doctor_id)
        cursor.execute(sql_query)

        sql_query = 'SELECT MAX(appointment_id) FROM appointment'
        cursor.execute(sql_query)
        appointment_id = cursor.fetchone()[0]
        result['appointment_id'] = appointment_id

        # Close connections
        cursor.close()
        con.commit()
        result['success'] = True
        return json.dumps(result)

    except Exception as e:
        # if the query or connection fails roll-back the transaction
        con.rollback()
        result['error'] = str(e)
        return json.dumps(result)
    finally:
        con.close()

@app.route('/appointment/<int:id>', methods=['DELETE'])
def delete_appointment(id):
    '''Deletes a previously created appointment'''
    result = dict()
    result['success'] = False
    appointment_id = id

    if appointment_id is None:
        result['error'] = 'appointment_id is not provided'
        return json.dumps(result)

    try:
        # Connect to database
        con = connect_database()
        cursor = con.cursor()

        # Add the appointment slot to availability
        sql_query = '''INSERT IGNORE INTO availability(doctor_id, date, time)
                        SELECT doctor_id, date, time FROM appointment WHERE appointment_id = {}'''\
                        .format(appointment_id)
        cursor.execute(sql_query)

        # Cancel the appointment
        sql_query = 'DELETE FROM appointment WHERE appointment_id = {}'.format(appointment_id)
        cursor.execute(sql_query)
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

@app.route('/login', methods=['POST'])
def user_login():
    '''Verify the user login'''
    result = dict()
    result['success'] = False

    username = request.form.get('username')
    password = request.form.get('password')

    # Check for null data
    if username is None:
        result['error'] = 'username is null'
        return json.dumps(result)
    elif password is None:
        result['error'] = 'password is null'
        return json.dumps(result)

    try:
        con = connect_database()
        cursor = con.cursor()

        # Get the id and name of the user
        sql_query = "SELECT profile_id, full_name as id FROM user_profile WHERE username='{}' and password = '{}'"\
                     .format(username, password)
        cursor.execute(sql_query)
        login_success = cursor.fetchone()

        # if user exists return details
        if login_success is None:
            return json.dumps(result)
        else:
            profile_id = login_success[0]
            full_name = login_success[1]
            sql_query = "SELECT 1 FROM customer WHERE profile_id={}".format(profile_id)
            cursor.execute(sql_query)

            # Determine user type
            if cursor.fetchone() is not None:
                result['user_type'] = 'customer'
            else:
                result['user_type'] = 'doctor'
            result['profile_id'] = profile_id
            result['full_name'] = full_name

        result['success'] = True
        return json.dumps(result)

    except Exception as e:
        con.rollback()
        return json.dumps(result)
    finally:
        con.close()

@app.route('/user', methods=['GET'])
def read_user():
    '''Returns information pertaining to a user'''
    result = dict()
    result['success'] = False

    id = request.args.get('id', None)
    user_type = request.args.get('user_type', None)

    # Check for null data
    if id is None or user_type is None:
        result['error'] = 'Either id or user_type is null.'
        return json.dumps(result)

    try:
        # Connect to database
        con = connect_database()
        cursor = con.cursor()

        # get doctor or customer info
        if user_type == 'doctor':
            sql_query = '''SELECT u.full_name, u.city, u.state, u.country, u.phone, u.email, u.photo_url,
                            u.address, d.experience, d.qualification,
                                (CASE WHEN AVG(r.score) IS NULL THEN 5
                                ELSE ROUND(AVG(r.score),0) END) AS score
                            FROM user_profile AS u
                            INNER JOIN doctor AS d ON u.profile_id=d.profile_id
                            LEFT OUTER JOIN reviews AS r ON d.doctor_id=r.doctor_id
                            WHERE d.profile_id = {}
                            GROUP BY d.doctor_id'''.format(int(id))
        else:
            sql_query = '''SELECT full_name, city, state, country, phone, email, photo_url, address
                            FROM user_profile
                            WHERE profile_id = {}'''\
                        .format(int(id))
        cursor.execute(sql_query)
        info = cursor.fetchone()

        info_dict = dict()
        info_dict['name'] = str(info[0])
        info_dict['city'] = str(info[1])
        info_dict['state'] = str(info[2])
        info_dict['country'] = str(info[3])
        info_dict['phone'] = str(info[4])
        info_dict['email'] = str(info[5])
        info_dict['photo_url'] = str(info[6])
        info_dict['address'] = str(info[7])
        if user_type == 'doctor':
            info_dict['experience'] = int(info[8])
            info_dict['qualification'] = str(info[9])
            info_dict['rating'] = int(info[10])
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
    '''Creates a new user account'''
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
        return json.dumps(result)
    elif user_type is None:
        result['error'] = 'User_Type is required'
        return json.dumps(result)

    try:
        # Connect to database
        con = connect_database()
        cursor = con.cursor()

        # check if user exists
        sql_query = "SELECT 1 FROM user_profile WHERE username='{}' or email = '{}'".format(username, email)
        cursor.execute(sql_query)
        print(sql_query)
        existing_user = cursor.fetchone()
        if existing_user is not None:
            result['error'] = 'User already exists'
            return json.dumps(result)

        # add record to user_profile
        sql_query = """INSERT INTO user_profile(username, password, email, phone, full_name,
                                              address, state, city, country)
                       VALUES('{}','{}','{}','{}','{}','{}','{}','{}','{}')"""\
                        .format(username, password, email, phone, full_name, address, state, city, country)
        print(sql_query)
        cursor.execute(sql_query)

        # Get the id of new profile created
        sql_query = "SELECT max(profile_id) FROM user_profile"
        cursor.execute(sql_query)
        profile_id = int(cursor.fetchone()[0])

        # If doctor then return address also
        if user_type == 'doctor':
            sql_query = "INSERT INTO doctor(profile_id, address) VALUES ({}, {})".format(profile_id, address)
        else:
            sql_query = "INSERT INTO customer(profile_id) VALUES ({})".format(profile_id)
        cursor.execute(sql_query)

        result['profile_id'] = profile_id

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

@app.route('/user/patient/<int:id>', methods=['DELETE'])
def delete_patient(id):
    '''Delete a patient record from database'''
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
        result['error'] = e
        return json.dumps(result)
    finally:
        con.close()

@app.route('/user/doctor/<int:id>', methods=['DELETE'])
def delete_doctor(id):
    '''Delete a doctor record from database'''
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
        result['error'] = str(e)
        return json.dumps(result)
    finally:
        con.close()

@app.route('/logout/<user_type>/<int:id>', methods=['POST'])
def user_logout(user_type, id):
    '''Logs out a user from application'''
    result = dict()
    result['success'] = True
    return json.dumps(result)

@app.route('/review', methods=['GET'])
def read_review():
    '''Reads list of reviews for a doctor'''
    result = dict()
    result['success'] = False

    profile_id = request.args.get('id', None)
    user_type = request.args.get('user_type', None)

    # Check for null data
    if profile_id is None or user_type is None:
        result['error'] = 'Either profile_id or user_type is null.'
        return json.dumps(result)
    elif user_type != 'doctor':
        result['error'] = 'Request should contain doctor as user_type.'
        return json.dumps(result)

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
        sql_query = "SELECT R.review_id, R.score, R.comment, U.full_name " \
                    "FROM reviews as R " \
                    "INNER JOIN customer as C ON R.customer_id=C.customer_id " \
                    "INNER JOIN user_profile as U ON C.profile_id=U.profile_id "\
                    "WHERE R.doctor_id={}".format(doctor_id)
        print(sql_query)
        cursor.execute(sql_query)
        reviews_iterator = cursor.fetchall()

        result['reviews'] = list()

        # Return list of reviews
        for review in reviews_iterator:
            review_dict = dict()
            review_dict['review_id'] = int(review[0])
            review_dict['score'] = int(review[1])
            review_dict['comment'] = str(review[2])
            review_dict['full_name'] = str(review[3])
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
    '''Creates a new review for a doctor'''
    result = dict()
    result['success'] = False

    customer_id = request.form.get('id')
    doctor_id = request.form.get('doctor_id')
    score = request.form.get('score')
    comment = request.form.get('comment') 

    print(comment)

    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

    # Check for null data
    if customer_id is None:
        result['error'] = 'Profile_id is null.'
        return json.dumps(result)
    elif score is None:
        result['error'] = '[Missing Score] Score for review is compulsory field.'
        return json.dumps(result)

    try:
        # Connect to database
        con = connect_database()
        cursor = con.cursor()

        # Insert review in reviews table
        sql_query = '''INSERT INTO reviews(score, comment, customer_id, doctor_id, date)
                        SELECT {}, '{}', c.customer_id, d.doctor_id, '{}'
                        FROM doctor d, customer c
                        WHERE c.profile_id = {} AND d.profile_id={}'''\
            .format(score, comment, timestamp, customer_id, doctor_id)
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

@app.route('/availability', methods=['GET'])
def read_availability():
    '''Read list of available slots for a doctor'''
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
        doctor_id = int(cursor.fetchone()[0])

        # Get list of reviews from reviews table
        sql_query ='''SELECT date, time FROM availability
                      WHERE doctor_id={} and DATE(date) > CURDATE()'''.format(doctor_id)
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
    """Create available slots for a doctor"""
    result = dict()
    result['success'] = False

    profile_id = request.form.get('id')
    available_slots = request.form.get('available_slots')

    # Check for null data
    if profile_id is None or available_slots is None:
        result['error'] = 'Either profile_id or available_slots is null.'
        return json.dumps(result)

    try:
        # Connect to database
        con = connect_database()
        cursor = con.cursor()

        # Unpack JSON from request
        availability_list = json.loads(available_slots)

        # Get doctor_id from doctor table
        sql_query = 'SELECT doctor_id FROM doctor WHERE profile_id={}'.format(profile_id)
        cursor.execute(sql_query)
        doctor_id = cursor.fetchone()
        doctor_id = int(doctor_id[0])

        # Check if the slots being provided have been already made available
        for slot in availability_list:
            date = slot['date']
            time = slot['time']
            sql_query = '''INSERT IGNORE INTO availability(doctor_id, date, time) VALUES({},'{}','{}')'''\
                        .format(doctor_id, date, time)
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
