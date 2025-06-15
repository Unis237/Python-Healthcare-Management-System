import streamlit as st
from datetime import datetime, time
import pandas as pd
import database as db
import patient
import doctor
import utils

# Utility: Verify if a medical test ID exists in the database
def verify_medical_test_id(medical_test_id):
    conn, c = db.connection()
    try:
        c.execute("SELECT id FROM medical_test_record;")
        ids = [row[0] for row in c.fetchall()]
    finally:
        c.close()
        conn.close()
    return medical_test_id in ids

# Utility: Display a list of medical test records using pandas
def show_medical_test_details(medical_tests):
    headers = [
        'Medical Test ID', 'Test name', 'Patient ID', 'Patient name',
        'Doctor ID', 'Doctor name', 'Medical Lab Scientist ID',
        'Test date and time [DD-MM-YYYY (hh:mm)]',
        'Result date and time [DD-MM-YYYY (hh:mm)]',
        'Result and diagnosis', 'Description', 'Comments', 'Cost (INR)'
    ]

    if not medical_tests:
        st.warning('No data to show')
    elif len(medical_tests) == 1:
        series = pd.Series(medical_tests[0], index=headers)
        st.write(series)
    else:
        df = pd.DataFrame(medical_tests, columns=headers)
        st.dataframe(df)

# Utility: Generate a unique Medical Test ID using current datetime
def generate_medical_test_id():
    now = datetime.now()
    return f'T-{now.strftime("%S%M%H")}-{now.strftime("%y%m%d")}'

# Utility: Get a patient or doctor name by ID
def get_patient_name(patient_id):
    conn, c = db.connection()
    try:
        c.execute("SELECT name FROM patient_record WHERE id = %(id)s;", {'id': patient_id})
        result = c.fetchone()
    finally:
        c.close()
        conn.close()
    return result[0] if result else None

def get_doctor_name(doctor_id):
    conn, c = db.connection()
    try:
        c.execute("SELECT name FROM doctor_record WHERE id = %(id)s;", {'id': doctor_id})
        result = c.fetchone()
    finally:
        c.close()
        conn.close()
    return result[0] if result else None

# Medical Test Class Definition
class Medical_Test:
    def __init__(self):
        self.id = ''
        self.test_name = ''
        self.patient_id = ''
        self.patient_name = ''
        self.doctor_id = ''
        self.doctor_name = ''
        self.medical_lab_scientist_id = ''
        self.test_date_time = ''
        self.result_date_time = ''
        self.cost = 0
        self.result_and_diagnosis = ''
        self.description = ''
        self.comments = ''

    # Add a new test record
    def add_medical_test(self):
        st.write('### Enter medical test details:')
        self.test_name = utils.sanitize_text_input(st.text_input('Test name'))

        # Patient ID verification
        patient_id = utils.sanitize_text_input(st.text_input('Patient ID'))
        if patient_id:
            if not patient.verify_patient_id(patient_id):
                st.error('Invalid Patient ID')
                return
            st.success('Verified')
            self.patient_id = patient_id
            self.patient_name = get_patient_name(patient_id)

        # Doctor ID verification
        doctor_id = utils.sanitize_text_input(st.text_input('Doctor ID'))
        if doctor_id:
            if not doctor.verify_doctor_id(doctor_id):
                st.error('Invalid Doctor ID')
                return
            st.success('Verified')
            self.doctor_id = doctor_id
            self.doctor_name = get_doctor_name(doctor_id)

        self.medical_lab_scientist_id = utils.sanitize_text_input(st.text_input('Medical lab scientist ID'))

        # Test datetime input
        test_date = st.date_input('Test date (YYYY/MM/DD)').strftime('%d-%m-%Y')
        test_time = st.time_input('Test time (hh:mm)', time(0, 0)).strftime('%H:%M')
        self.test_date_time = f'{test_date} ({test_time})'

        # Result datetime input
        result_date = st.date_input('Result date (YYYY/MM/DD)').strftime('%d-%m-%Y')
        result_time = st.time_input('Result time (hh:mm)', time(0, 0)).strftime('%H:%M')
        self.result_date_time = f'{result_date} ({result_time})'

        # Cost and textual fields
        self.cost = st.number_input('Cost (INR)', value=0, min_value=0, max_value=10000)
        self.result_and_diagnosis = utils.sanitize_text_input(st.text_area('Result and diagnosis')) or 'Test result awaited'
        self.description = utils.sanitize_text_input(st.text_area('Description')) or None
        self.comments = utils.sanitize_text_input(st.text_area('Comments (if any)')) or None
        self.id = generate_medical_test_id()

        if st.button('Save'):
            try:
                conn, c = db.connection()
                with conn:
                    c.execute("""
                        INSERT INTO medical_test_record (
                            id, test_name, patient_id, patient_name,
                            doctor_id, doctor_name, medical_lab_scientist_id,
                            test_date_time, result_date_time, cost,
                            result_and_diagnosis, description, comments
                        ) VALUES (
                            %(id)s, %(name)s, %(p_id)s, %(p_name)s, %(dr_id)s, %(dr_name)s,
                            %(mls_id)s, %(test_date_time)s, %(result_date_time)s,
                            %(cost)s, %(result_diagnosis)s, %(desc)s, %(comments)s
                        );
                    """, {
                        'id': self.id, 'name': self.test_name,
                        'p_id': self.patient_id, 'p_name': self.patient_name,
                        'dr_id': self.doctor_id, 'dr_name': self.doctor_name,
                        'mls_id': self.medical_lab_scientist_id,
                        'test_date_time': self.test_date_time,
                        'result_date_time': self.result_date_time,
                        'cost': self.cost,
                        'result_diagnosis': self.result_and_diagnosis,
                        'desc': self.description,
                        'comments': self.comments
                    })
                st.success('Medical test details saved successfully.')
                st.write('The Medical Test ID is:', self.id)
            except Exception as e:
                st.error(f'Error saving medical test details: {e}')
            finally:
                c.close()
                conn.close()

    # Update an existing test record
    def update_medical_test(self):
        id = utils.sanitize_text_input(st.text_input('Enter Medical Test ID to update'))
        if not id:
            return
        if not verify_medical_test_id(id):
            st.error('Invalid Medical Test ID')
            return

        st.success('Verified')
        try:
            conn, c = db.connection()
            with conn:
                c.execute("SELECT * FROM medical_test_record WHERE id = %(id)s;", {'id': id})
                st.write('Current medical test details:')
                show_medical_test_details(c.fetchall())

            st.write('### Enter new details:')
            self.result_and_diagnosis = utils.sanitize_text_input(st.text_area('Result and diagnosis')) or 'Test result awaited'
            self.description = utils.sanitize_text_input(st.text_area('Description')) or None
            self.comments = utils.sanitize_text_input(st.text_area('Comments (if any)')) or None

            if st.button('Update'):
                with conn:
                    c.execute("""
                        UPDATE medical_test_record
                        SET result_and_diagnosis = %(result_diagnosis)s,
                            description = %(description)s,
                            comments = %(comments)s
                        WHERE id = %(id)s;
                    """, {
                        'id': id,
                        'result_diagnosis': self.result_and_diagnosis,
                        'description': self.description,
                        'comments': self.comments
                    })
                st.success('Medical test details updated successfully.')
        except Exception as e:
            st.error(f'Error updating medical test details: {e}')
        finally:
            c.close()
            conn.close()

    # Delete a test record
    def delete_medical_test(self):
        id = utils.sanitize_text_input(st.text_input('Enter Medical Test ID to delete'))
        if not id:
            return
        if not verify_medical_test_id(id):
            st.error('Invalid Medical Test ID')
            return

        st.success('Verified')
        try:
            conn, c = db.connection()
            with conn:
                c.execute("SELECT * FROM medical_test_record WHERE id = %(id)s;", {'id': id})
                st.write('Details of the medical test to be deleted:')
                show_medical_test_details(c.fetchall())

                if st.checkbox('Check this box to confirm that you want to delete this record'):
                    if st.button('Delete'):
                        c.execute("DELETE FROM medical_test_record WHERE id = %(id)s;", {'id': id})
                        st.success('Medical test details deleted successfully.')
        except Exception as e:
            st.error(f'Error deleting medical test details: {e}')
        finally:
            c.close()
            conn.close()

    # View test records by patient ID
    def medical_tests_by_patient(self):
        patient_id = utils.sanitize_text_input(st.text_input('Enter Patient ID to view all their medical test records'))
        if not patient_id:
            return
        if not patient.verify_patient_id(patient_id):
            st.error('Invalid Patient ID')
            return

        st.success('Verified')
        try:
            conn, c = db.connection()
            with conn:
                c.execute("SELECT * FROM medical_test_record WHERE patient_id = %(p_id)s;", {'p_id': patient_id})
                st.write(f'Medical test record for {get_patient_name(patient_id)}:')
                show_medical_test_details(c.fetchall())
        except Exception as e:
            st.error(f'Error fetching medical test records: {e}')
        finally:
            c.close()
            conn.close()
