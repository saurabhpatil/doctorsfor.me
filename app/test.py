import routes
import unittest 
import requests

class RoutesTestCase(unittest.TestCase):
    
    def setUp(self):
        self.con = routes.connect_database()

    def tearDown(self):
        self.con.close()

    def test_delete_patient(self):
        cursor = self.con.cursor()
        
        insert_query = "INSERT INTO user_profile(username, password, email, phone, full_name, state, city, country) VALUES('test_patient','test','test@email.com','1234567890','Test User','Texas','Austin','USA')"
        # print(insert_query)
        cursor.execute(insert_query)

        insert_query = "INSERT INTO user_profile(username, password, email, phone, full_name, state, city, country) VALUES('test_doctor','test','test1@email.com','1234567890','Test User','Texas','Austin','USA')"
        # print(insert_query)
        cursor.execute(insert_query)

        sql_query = "SELECT profile_id FROM user_profile WHERE username='test_patient'"
        # print(sql_query)
        cursor.execute(sql_query)
        patient_profile_id = cursor.fetchone()
        patient_profile_id = int(patient_profile_id[0])
        # print(int(profile_id))
        self.assertIsNotNone(patient_profile_id)

        sql_query = "SELECT profile_id FROM user_profile WHERE username='test_doctor'"
        # print(sql_query)
        cursor.execute(sql_query)
        doctor_profile_id = cursor.fetchone()
        doctor_profile_id = int(doctor_profile_id[0])
        # print(int(profile_id))
        self.assertIsNotNone(doctor_profile_id)

        insert_query = "INSERT INTO customer(profile_id) VALUES({})".format(patient_profile_id)
        # print(insert_query)
        cursor.execute(insert_query)

        sql_query = "SELECT customer_id FROM customer WHERE profile_id={}".format(patient_profile_id)
        # print(sql_query)
        cursor.execute(sql_query)
        patient_id = cursor.fetchone()
        patient_id = int(patient_id[0])
        self.assertIsNotNone(patient_id)

        insert_query = "INSERT INTO doctor(profile_id, experience, type, qualification, total_rating, address) VALUES({}, 17, 'Dentist', 'MD', 5.0, 'Austin')".format(doctor_profile_id)
        # print(insert_query)
        cursor.execute(insert_query)

        sql_query = "SELECT doctor_id FROM doctor WHERE profile_id='{}'".format(doctor_profile_id)
        # print(sql_query)
        cursor.execute(sql_query)
        doctor_id = cursor.fetchone()
        doctor_id = int(doctor_id[0])
        self.assertIsNotNone(doctor_id)

        insert_query = "INSERT INTO appointment(customer_id, doctor_id, date, time) VALUES({}, {}, '20170320', '1200')".format(patient_id, doctor_id)
        # print(insert_query)
        cursor.execute(insert_query)

        # Delete temp doctor and user_profile
        sql_query = 'DELETE FROM appointment WHERE doctor_id={}'.format(doctor_id)
        cursor.execute(sql_query)

        sql_query = 'DELETE FROM doctor WHERE profile_id={}'.format(doctor_profile_id)
        cursor.execute(sql_query)

        sql_query = 'DELETE FROM user_profile WHERE profile_id={}'.format(doctor_profile_id)
        cursor.execute(sql_query)

        self.con.commit()

        resp = requests.delete('http://localhost:5000/user/patient/'+str(patient_profile_id))
        result = resp.json()
        self.assertTrue(result['success'])


    def test_delete_doctor(self):
        cursor = self.con.cursor()
        
        insert_query = "INSERT INTO user_profile(username, password, email, phone, full_name, state, city, country) VALUES('test_patient','test','test@email.com','1234567890','Test User','Texas','Austin','USA')"
        # print(insert_query)
        cursor.execute(insert_query)

        insert_query = "INSERT INTO user_profile(username, password, email, phone, full_name, state, city, country) VALUES('test_doctor','test','test1@email.com','1234567890','Test User','Texas','Austin','USA')"
        # print(insert_query)
        cursor.execute(insert_query)

        sql_query = "SELECT profile_id FROM user_profile WHERE username='test_patient'"
        # print(sql_query)
        cursor.execute(sql_query)
        patient_profile_id = cursor.fetchone()
        patient_profile_id = int(patient_profile_id[0])
        # print(int(profile_id))
        self.assertIsNotNone(patient_profile_id)

        sql_query = "SELECT profile_id FROM user_profile WHERE username='test_doctor'"
        # print(sql_query)
        cursor.execute(sql_query)
        doctor_profile_id = cursor.fetchone()
        doctor_profile_id = int(doctor_profile_id[0])
        # print(int(profile_id))
        self.assertIsNotNone(doctor_profile_id)

        insert_query = "INSERT INTO customer(profile_id) VALUES({})".format(patient_profile_id)
        # print(insert_query)
        cursor.execute(insert_query)

        sql_query = "SELECT customer_id FROM customer WHERE profile_id={}".format(patient_profile_id)
        # print(sql_query)
        cursor.execute(sql_query)
        patient_id = cursor.fetchone()
        patient_id = int(patient_id[0])
        self.assertIsNotNone(patient_id)

        insert_query = "INSERT INTO doctor(profile_id, experience, type, qualification, total_rating, address) VALUES({}, 17, 'Dentist', 'MD', 5.0, 'Austin')".format(doctor_profile_id)
        # print(insert_query)
        cursor.execute(insert_query)

        sql_query = "SELECT doctor_id FROM doctor WHERE profile_id='{}'".format(doctor_profile_id)
        # print(sql_query)
        cursor.execute(sql_query)
        doctor_id = cursor.fetchone()
        doctor_id = int(doctor_id[0])
        self.assertIsNotNone(doctor_id)

        insert_query = "INSERT INTO appointment(customer_id, doctor_id, date, time) VALUES({}, {}, '20170320', '1200')".format(patient_id, doctor_id)
        # print(insert_query)
        cursor.execute(insert_query)

        # Delete temp doctor and user_profile
        sql_query = 'DELETE FROM appointment WHERE customer_id={}'.format(patient_id)
        cursor.execute(sql_query)

        sql_query = 'DELETE FROM customer WHERE profile_id={}'.format(patient_profile_id)
        cursor.execute(sql_query)

        sql_query = 'DELETE FROM user_profile WHERE profile_id={}'.format(patient_profile_id)
        cursor.execute(sql_query)

        self.con.commit()

        resp = requests.delete('http://localhost:5000/user/doctor/'+str(doctor_profile_id))
        result = resp.json()
        self.assertTrue(result['success'])

    def test_logout(self):
        resp = requests.post('http://localhost:5000/logout/doctor/12345')
        result = resp.json()
        self.assertTrue(result['success'])

