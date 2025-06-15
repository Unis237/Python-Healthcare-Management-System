import streamlit as st
from datetime import datetime
import database as db
import pandas as pd
import patient
import doctor
import utils

# Utility functions
def verify_prescription_id(prescription_id):
    conn, c = db.connection()
    try:
        c.execute("SELECT id FROM prescription_record WHERE id = %(id)s", {'id': prescription_id})
        return c.fetchone() is not None
    finally:
        c.close()
        conn.close()

def show_prescription_details(prescriptions):
    titles = [
        'Prescription ID', 'Patient ID', 'Patient name', 'Doctor ID', 'Doctor name',
        'Diagnosis', 'Comments', 'Medicine 1 name', 'Medicine 1 dosage and description',
        'Medicine 2 name', 'Medicine 2 dosage and description', 'Medicine 3 name',
        'Medicine 3 dosage and description'
    ]
    if not prescriptions:
        st.warning('No data to show.')
    elif len(prescriptions) == 1:
        st.write(pd.Series(data=prescriptions[0], index=titles))
    else:
        df = pd.DataFrame(data=prescriptions, columns=titles)
        st.write(df)

def generate_prescription_id():
    return f'M-{datetime.now().strftime("%S%M%H")}-{datetime.now().strftime("%y%m%d")}'

def get_name_by_id(table, user_id):
    conn, c = db.connection()
    try:
        c.execute(f"SELECT name FROM {table} WHERE id = %(id)s", {'id': user_id})
        result = c.fetchone()
        return result[0] if result else None
    finally:
        c.close()
        conn.close()

# Class definition
class Prescription:

    def __init__(self):
        self.clear()

    def clear(self):
        self.id = ""
        self.patient_id = ""
        self.patient_name = ""
        self.doctor_id = ""
        self.doctor_name = ""
        self.diagnosis = ""
        self.comments = None
        self.medicine_1_name = ""
        self.medicine_1_dosage_description = ""
        self.medicine_2_name = None
        self.medicine_2_dosage_description = None
        self.medicine_3_name = None
        self.medicine_3_dosage_description = None

    def input_prescription_fields(self, update=False):
        self.diagnosis = utils.sanitize_text_input(st.text_area('Diagnosis'))
        self.comments = utils.sanitize_text_input(st.text_area('Comments (if any)')) or None
        self.medicine_1_name = utils.sanitize_text_input(st.text_input('Medicine 1 name'))
        self.medicine_1_dosage_description = utils.sanitize_text_input(st.text_area('Medicine 1 dosage and description'))
        self.medicine_2_name = utils.sanitize_text_input(st.text_input('Medicine 2 name (optional)')) or None
        self.medicine_2_dosage_description = utils.sanitize_text_input(st.text_area('Medicine 2 dosage and description')) or None
        self.medicine_3_name = utils.sanitize_text_input(st.text_input('Medicine 3 name (optional)')) or None
        self.medicine_3_dosage_description = utils.sanitize_text_input(st.text_area('Medicine 3 dosage and description')) or None

    def add_prescription(self):
        st.subheader('Enter prescription details:')
        self.patient_id = utils.sanitize_text_input(st.text_input('Patient ID'))
        if self.patient_id and not patient.verify_patient_id(self.patient_id):
            st.error('Invalid Patient ID.')
            return
        elif self.patient_id:
            self.patient_name = get_name_by_id("patient_record", self.patient_id)
            st.success(f"Patient verified: {self.patient_name}")

        self.doctor_id = utils.sanitize_text_input(st.text_input('Doctor ID'))
        if self.doctor_id and not doctor.verify_doctor_id(self.doctor_id):
            st.error('Invalid Doctor ID.')
            return
        elif self.doctor_id:
            self.doctor_name = get_name_by_id("doctor_record", self.doctor_id)
            st.success(f"Doctor verified: {self.doctor_name}")

        self.input_prescription_fields()
        self.id = generate_prescription_id()

        if st.button('Save'):
            try:
                conn, c = db.connection()
                c.execute("""
                    INSERT INTO prescription_record (
                        id, patient_id, patient_name, doctor_id, doctor_name,
                        diagnosis, comments, medicine_1_name, medicine_1_dosage_description,
                        medicine_2_name, medicine_2_dosage_description, medicine_3_name,
                        medicine_3_dosage_description
                    ) VALUES (
                        %(id)s, %(patient_id)s, %(patient_name)s, %(doctor_id)s, %(doctor_name)s,
                        %(diagnosis)s, %(comments)s, %(med1_name)s, %(med1_desc)s,
                        %(med2_name)s, %(med2_desc)s, %(med3_name)s, %(med3_desc)s
                    );
                """, {
                    'id': self.id, 'patient_id': self.patient_id, 'patient_name': self.patient_name,
                    'doctor_id': self.doctor_id, 'doctor_name': self.doctor_name,
                    'diagnosis': self.diagnosis, 'comments': self.comments,
                    'med1_name': self.medicine_1_name, 'med1_desc': self.medicine_1_dosage_description,
                    'med2_name': self.medicine_2_name, 'med2_desc': self.medicine_2_dosage_description,
                    'med3_name': self.medicine_3_name, 'med3_desc': self.medicine_3_dosage_description
                })
                conn.commit()
                st.success(f'Prescription saved. ID: {self.id}')
            except Exception as e:
                st.error(f'Error saving prescription details: {e}')
            finally:
                conn.close()

    def update_prescription(self):
        id = utils.sanitize_text_input(st.text_input('Enter Prescription ID to update'))
        if not id:
            return
        if not verify_prescription_id(id):
            st.error('Invalid Prescription ID.')
            return

        st.success('Verified')
        try:
            conn, c = db.connection()
            c.execute("SELECT * FROM prescription_record WHERE id = %(id)s", {'id': id})
            st.write('Current details:')
            show_prescription_details(c.fetchall())

            st.subheader('Enter new details:')
            self.input_prescription_fields(update=True)

            if st.button('Update'):
                c.execute("""
                    UPDATE prescription_record
                    SET diagnosis = %(diagnosis)s, comments = %(comments)s,
                        medicine_1_name = %(med1_name)s, medicine_1_dosage_description = %(med1_desc)s,
                        medicine_2_name = %(med2_name)s, medicine_2_dosage_description = %(med2_desc)s,
                        medicine_3_name = %(med3_name)s, medicine_3_dosage_description = %(med3_desc)s
                    WHERE id = %(id)s;
                """, {
                    'id': id, 'diagnosis': self.diagnosis, 'comments': self.comments,
                    'med1_name': self.medicine_1_name, 'med1_desc': self.medicine_1_dosage_description,
                    'med2_name': self.medicine_2_name, 'med2_desc': self.medicine_2_dosage_description,
                    'med3_name': self.medicine_3_name, 'med3_desc': self.medicine_3_dosage_description
                })
                conn.commit()
                st.success('Prescription updated successfully.')
        except Exception as e:
            st.error(f'Error updating prescription details: {e}')
        finally:
            conn.close()

    def delete_prescription(self):
        id = utils.sanitize_text_input(st.text_input('Enter Prescription ID to delete'))
        if not id:
            return
        if not verify_prescription_id(id):
            st.error('Invalid Prescription ID.')
            return

        st.success('Verified')
        try:
            conn, c = db.connection()
            c.execute("SELECT * FROM prescription_record WHERE id = %(id)s", {'id': id})
            st.write('Prescription to be deleted:')
            show_prescription_details(c.fetchall())

            if st.checkbox('Confirm deletion') and st.button('Delete'):
                c.execute("DELETE FROM prescription_record WHERE id = %(id)s", {'id': id})
                conn.commit()
                st.success('Prescription deleted successfully.')
        except Exception as e:
            st.error(f'Error deleting prescription details: {e}')
        finally:
            conn.close()

    def prescriptions_by_patient(self):
        patient_id = utils.sanitize_text_input(st.text_input('Enter Patient ID'))
        if not patient_id:
            return
        if not patient.verify_patient_id(patient_id):
            st.error('Invalid Patient ID.')
            return

        st.success('Verified')
        try:
            conn, c = db.connection()
            c.execute("SELECT * FROM prescription_record WHERE patient_id = %(id)s", {'id': patient_id})
            prescriptions = c.fetchall()
            st.write(f'Prescriptions for {get_name_by_id("patient_record", patient_id)}:')
            show_prescription_details(prescriptions)
        except Exception as e:
            st.error(f'Error fetching prescription records: {e}')
        finally:
            conn.close()
