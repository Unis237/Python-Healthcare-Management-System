import streamlit as st
from datetime import datetime, date
import database as db
import pandas as pd
import department
import utils

def verify_doctor_id(doctor_id):
    verify = False
    conn, c = db.connection()
    try:
        c.execute("SELECT id FROM doctor_record;")
        for id in c.fetchall():
            if id[0] == doctor_id:
                verify = True
                break
    finally:
        c.close()
        conn.close()
    return verify

def show_doctor_details(list_of_doctors):
    doctor_titles = [
        'Doctor ID', 'Name', 'Age', 'Gender', 'Date of birth (DD-MM-YYYY)',
        'Blood group', 'Department ID', 'Department name',
        'Contact number', 'Alternate contact number', 'Aadhar ID / Voter ID',
        'Email ID', 'Qualification', 'Specialisation',
        'Years of experience', 'Address', 'City', 'State', 'PIN code'
    ]
    if len(list_of_doctors) == 0:
        st.warning('No data to show')
    elif len(list_of_doctors) == 1:
        series = pd.Series(data=list_of_doctors[0], index=doctor_titles)
        st.write(series)
    else:
        df = pd.DataFrame(data=list_of_doctors, columns=doctor_titles)
        st.write(df)

def calculate_age(dob):
    today = date.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    return age

def generate_doctor_id():
    now = datetime.now()
    id_1 = now.strftime('%S%M%H')
    id_2 = now.strftime('%Y%m%d')[2:]
    return f'DR-{id_1}-{id_2}'

def get_department_name(dept_id):
    conn, c = db.connection()
    try:
        c.execute(
            "SELECT name FROM department_record WHERE id = %s;", (dept_id,)
        )
        result = c.fetchone()
        return result[0] if result else None
    finally:
        c.close()
        conn.close()

class Doctor:
    def __init__(self):
        self.name = ''
        self.id = ''
        self.age = 0
        self.gender = ''
        self.date_of_birth = ''
        self.blood_group = ''
        self.department_id = ''
        self.department_name = ''
        self.contact_number_1 = ''
        self.contact_number_2 = ''
        self.aadhar_or_voter_id = ''
        self.email_id = ''
        self.qualification = ''
        self.specialisation = ''
        self.years_of_experience = 0
        self.address = ''
        self.city = ''
        self.state = ''
        self.pin_code = ''

    def add_doctor(self):
        st.write('Enter doctor details:')
        self.name = utils.sanitize_text_input(st.text_input('Full name'))
        gender = st.radio('Gender', ['Female', 'Male', 'Other'])
        self.gender = utils.sanitize_text_input(st.text_input('Please mention')) if gender == 'Other' else gender

        dob = st.date_input('Date of birth (YYYY/MM/DD)')
        st.info('If the required date is not in the calendar, please type it in the box above.')
        self.date_of_birth = dob.strftime('%d-%m-%Y')
        self.age = calculate_age(dob)

        self.blood_group = utils.sanitize_text_input(st.text_input('Blood group'))

        department_id = utils.sanitize_text_input(st.text_input('Department ID'))
        if department_id:
            if department.verify_department_id(department_id):
                st.success('Verified')
                self.department_id = department_id
                self.department_name = get_department_name(department_id)
            else:
                st.error('Invalid Department ID')

        self.contact_number_1 = utils.sanitize_text_input(st.text_input('Contact number'))
        contact_number_2 = st.text_input('Alternate contact number (optional)')
        self.contact_number_2 = utils.sanitize_text_input(contact_number_2) if contact_number_2 else None
        self.aadhar_or_voter_id = utils.sanitize_text_input(st.text_input('Aadhar ID / Voter ID'))
        self.email_id = utils.sanitize_text_input(st.text_input('Email ID'))
        self.qualification = utils.sanitize_text_input(st.text_input('Qualification'))
        self.specialisation = utils.sanitize_text_input(st.text_input('Specialisation'))
        self.years_of_experience = st.number_input('Years of experience', value=0, min_value=0, max_value=100)
        self.address = utils.sanitize_text_input(st.text_area('Address'))
        self.city = utils.sanitize_text_input(st.text_input('City'))
        self.state = utils.sanitize_text_input(st.text_input('State'))
        self.pin_code = utils.sanitize_text_input(st.text_input('PIN code'))
        self.id = generate_doctor_id()

        # Validate email and phone numbers
        valid_email = utils.validate_email(self.email_id)
        valid_phone_1 = utils.validate_phone_number(self.contact_number_1)
        valid_phone_2 = utils.validate_phone_number(self.contact_number_2)

        if not valid_email:
            st.error('Invalid email format.')
            return
        if not valid_phone_1:
            st.error('Invalid contact number format.')
            return
        if self.contact_number_2 and not valid_phone_2:
            st.error('Invalid alternate contact number format.')
            return

        if st.button('Save'):
            conn, c = db.connection()
            try:
                c.execute(
                    """
                    INSERT INTO doctor_record (
                        id, name, age, gender, date_of_birth, blood_group,
                        department_id, department_name, contact_number_1,
                        contact_number_2, aadhar_or_voter_id, email_id,
                        qualification, specialisation, years_of_experience,
                        address, city, state, pin_code
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                    """,
                    (
                        self.id, self.name, self.age, self.gender, self.date_of_birth,
                        self.blood_group, self.department_id, self.department_name,
                        self.contact_number_1, self.contact_number_2,
                        self.aadhar_or_voter_id, self.email_id, self.qualification,
                        self.specialisation, self.years_of_experience,
                        self.address, self.city, self.state, self.pin_code
                    )
                )
                conn.commit()
                st.success('Doctor details saved successfully.')
                st.write('Your Doctor ID is: ', self.id)
            except Exception as e:
                conn.rollback()
                st.error(f'Error saving doctor details: {e}')
            finally:
                c.close()
                conn.close()

    def update_doctor(self):
        id = utils.sanitize_text_input(st.text_input('Enter Doctor ID of the doctor to be updated'))
        if id and verify_doctor_id(id):
            st.success('Verified')
            conn, c = db.connection()
            try:
                c.execute("SELECT * FROM doctor_record WHERE id = %s;", (id,))
                st.write('Here are the current details of the doctor:')
                show_doctor_details(c.fetchall())

                st.write('Enter new details of the doctor:')
                department_id = utils.sanitize_text_input(st.text_input('Department ID'))
                if department_id:
                    if department.verify_department_id(department_id):
                        st.success('Verified')
                        self.department_id = department_id
                        self.department_name = get_department_name(department_id)
                    else:
                        st.error('Invalid Department ID')

                self.contact_number_1 = utils.sanitize_text_input(st.text_input('Contact number'))
                contact_number_2 = st.text_input('Alternate contact number (optional)')
                self.contact_number_2 = utils.sanitize_text_input(contact_number_2) if contact_number_2 else None
                self.email_id = utils.sanitize_text_input(st.text_input('Email ID'))
                self.qualification = utils.sanitize_text_input(st.text_input('Qualification'))
                self.specialisation = utils.sanitize_text_input(st.text_input('Specialisation'))
                self.years_of_experience = st.number_input('Years of experience', value=0, min_value=0, max_value=100)
                self.address = utils.sanitize_text_input(st.text_area('Address'))
                self.city = utils.sanitize_text_input(st.text_input('City'))
                self.state = utils.sanitize_text_input(st.text_input('State'))
                self.pin_code = utils.sanitize_text_input(st.text_input('PIN code'))

                # Validate email and phone numbers
                valid_email = utils.validate_email(self.email_id)
                valid_phone_1 = utils.validate_phone_number(self.contact_number_1)
                valid_phone_2 = utils.validate_phone_number(self.contact_number_2)

                if not valid_email:
                    st.error('Invalid email format.')
                    return
                if not valid_phone_1:
                    st.error('Invalid contact number format.')
                    return
                if self.contact_number_2 and not valid_phone_2:
                    st.error('Invalid alternate contact number format.')
                    return

                if st.button('Update'):
                    c.execute("SELECT date_of_birth FROM doctor_record WHERE id = %s;", (id,))
                    dob_str = c.fetchone()[0]
                    dob = datetime.strptime(dob_str, '%d-%m-%Y').date()
                    self.age = calculate_age(dob)

                    c.execute(
                        """
                        UPDATE doctor_record
                        SET age = %s, department_id = %s, department_name = %s,
                            contact_number_1 = %s, contact_number_2 = %s,
                            email_id = %s, qualification = %s, specialisation = %s,
                            years_of_experience = %s, address = %s,
                            city = %s, state = %s, pin_code = %s
                        WHERE id = %s;
                        """,
                        (
                            self.age, self.department_id, self.department_name,
                            self.contact_number_1, self.contact_number_2,
                            self.email_id, self.qualification, self.specialisation,
                            self.years_of_experience, self.address, self.city,
                            self.state, self.pin_code, id
                        )
                    )
                    conn.commit()
                    st.success('Doctor details updated successfully.')
            except Exception as e:
                conn.rollback()
                st.error(f'Error updating doctor details: {e}')
            finally:
                c.close()
                conn.close()

    def delete_doctor(self):
        id = utils.sanitize_text_input(st.text_input('Enter Doctor ID of the doctor to be deleted'))
        if id and verify_doctor_id(id):
            st.success('Verified')
            conn, c = db.connection()
            try:
                c.execute("SELECT * FROM doctor_record WHERE id = %s;", (id,))
                st.write('Here are the details of the doctor to be deleted:')
                show_doctor_details(c.fetchall())

                if st.checkbox('Check this box to confirm deletion') and st.button('Delete'):
                    c.execute("DELETE FROM doctor_record WHERE id = %s;", (id,))
                    conn.commit()
                    st.success('Doctor details deleted successfully.')
            except Exception as e:
                conn.rollback()
                st.error(f'Error deleting doctor details: {e}')
            finally:
                c.close()
                conn.close()

    def show_all_doctors(self):
        conn, c = db.connection()
        try:
            c.execute("SELECT * FROM doctor_record;")
            show_doctor_details(c.fetchall())
        finally:
            c.close()
            conn.close()

    def search_doctor(self):
        id = utils.sanitize_text_input(st.text_input('Enter Doctor ID of the doctor to be searched'))
        if id and verify_doctor_id(id):
            st.success('Verified')
            conn, c = db.connection()
            try:
                c.execute("SELECT * FROM doctor_record WHERE id = %s;", (id,))
                st.write('Here are the details of the doctor you searched for:')
                show_doctor_details(c.fetchall())
            finally:
                c.close()
                conn.close()
