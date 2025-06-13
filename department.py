import streamlit as st
from datetime import datetime
import database as db
import pandas as pd

# function to verify department id
def verify_department_id(department_id):
    verify = False
    conn, c = db.connection()
    with conn:
        c.execute("SELECT id FROM department_record;")
        department_ids = c.fetchall()
    for id in department_ids:
        if id[0] == department_id:
            verify = True
            break
    conn.close()
    return verify

# function to show the details of department(s) given in a list (provided as a parameter)
def show_department_details(list_of_departments):
    department_titles = ['Department ID', 'Department name', 'Description', 'Contact number',
                         'Alternate contact number', 'Address', 'Email ID']
    if len(list_of_departments) == 0:
        st.warning('No data to show')
    elif len(list_of_departments) == 1:
        series = pd.Series(data=list_of_departments[0], index=department_titles)
        st.write(series)
    else:
        df = pd.DataFrame(data=list_of_departments, columns=department_titles)
        st.write(df)

# function to generate unique department id using current date and time
def generate_department_id():
    now = datetime.now()
    id_1 = now.strftime('%S%M%H')
    id_2 = now.strftime('%Y%m%d')[2:]
    return f'D-{id_1}-{id_2}'

# function to show the doctor id and name of doctor(s) given in a list (provided as a parameter)
def show_list_of_doctors(list_of_doctors):
    doctor_titles = ['Doctor ID', 'Name']
    if len(list_of_doctors) == 0:
        st.warning('No data to show')
    else:
        df = pd.DataFrame(data=list_of_doctors, columns=doctor_titles)
        st.write(df)

# function to fetch department name from the database for the given department id
def get_department_name(dept_id):
    conn, c = db.connection()
    with conn:
        c.execute(
            """
            SELECT name
            FROM department_record
            WHERE id = %(id)s;
            """,
            {'id': dept_id}
        )
        result = c.fetchone()
    conn.close()
    return result[0] if result else 'Unknown'

# class containing all the fields and methods required to work with the departments' table in the database
class Department:

    def __init__(self):
        self.name = ""
        self.id = ""
        self.description = ""
        self.contact_number_1 = ""
        self.contact_number_2 = ""
        self.address = ""
        self.email_id = ""

    def add_department(self):
        st.write('Enter department details:')
        self.name = st.text_input('Department name')
        self.description = st.text_area('Description')
        self.contact_number_1 = st.text_input('Contact number')
        contact_number_2 = st.text_input('Alternate contact number (optional)')
        self.contact_number_2 = contact_number_2 if contact_number_2 else None
        self.address = st.text_area('Address')
        self.email_id = st.text_input('Email ID')
        self.id = generate_department_id()
        save = st.button('Save')

        if save:
            conn, c = db.connection()
            with conn:
                c.execute(
                    """
                    INSERT INTO department_record (
                        id, name, description, contact_number_1, contact_number_2,
                        address, email_id
                    )
                    VALUES (
                        %(id)s, %(name)s, %(desc)s, %(phone_1)s, %(phone_2)s, %(address)s, %(email_id)s
                    );
                    """,
                    {
                        'id': self.id, 'name': self.name, 'desc': self.description,
                        'phone_1': self.contact_number_1,
                        'phone_2': self.contact_number_2, 'address': self.address,
                        'email_id': self.email_id
                    }
                )
            st.success('Department details saved successfully.')
            st.write('The Department ID is: ', self.id)
            conn.close()

    def update_department(self):
        id = st.text_input('Enter Department ID of the department to be updated')
        if not id:
            return
        elif not verify_department_id(id):
            st.error('Invalid Department ID')
        else:
            st.success('Verified')
            conn, c = db.connection()
            with conn:
                c.execute(
                    """
                    SELECT *
                    FROM department_record
                    WHERE id = %(id)s;
                    """,
                    {'id': id}
                )
                department_data = c.fetchall()
            st.write('Here are the current details of the department:')
            show_department_details(department_data)

            st.write('Enter new details of the department:')
            self.description = st.text_area('Description')
            self.contact_number_1 = st.text_input('Contact number')
            contact_number_2 = st.text_input('Alternate contact number (optional)')
            self.contact_number_2 = contact_number_2 if contact_number_2 else None
            self.address = st.text_area('Address')
            self.email_id = st.text_input('Email ID')
            update = st.button('Update')

            if update:
                with conn:
                    c.execute(
                        """
                        UPDATE department_record
                        SET description = %(desc)s,
                            contact_number_1 = %(phone_1)s,
                            contact_number_2 = %(phone_2)s,
                            address = %(address)s,
                            email_id = %(email_id)s
                        WHERE id = %(id)s;
                        """,
                        {
                            'id': id, 'desc': self.description,
                            'phone_1': self.contact_number_1,
                            'phone_2': self.contact_number_2,
                            'address': self.address, 'email_id': self.email_id
                        }
                    )
                st.success('Department details updated successfully.')
                conn.close()

    def delete_department(self):
        id = st.text_input('Enter Department ID of the department to be deleted')
        if not id:
            return
        elif not verify_department_id(id):
            st.error('Invalid Department ID')
        else:
            st.success('Verified')
            conn, c = db.connection()
            with conn:
                c.execute(
                    """
                    SELECT *
                    FROM department_record
                    WHERE id = %(id)s;
                    """,
                    {'id': id}
                )
                department_data = c.fetchall()
            st.write('Here are the details of the department to be deleted:')
            show_department_details(department_data)

            confirm = st.checkbox('Check this box to confirm deletion')
            if confirm:
                delete = st.button('Delete')
                if delete:
                    with conn:
                        c.execute(
                            """
                            DELETE FROM department_record
                            WHERE id = %(id)s;
                            """,
                            {'id': id}
                        )
                    st.success('Department details deleted successfully.')
            conn.close()

    def show_all_departments(self):
        conn, c = db.connection()
        with conn:
            c.execute("SELECT * FROM department_record;")
            departments = c.fetchall()
        show_department_details(departments)
        conn.close()

    def search_department(self):
        id = st.text_input('Enter Department ID of the department to be searched')
        if not id:
            return
        elif not verify_department_id(id):
            st.error('Invalid Department ID')
        else:
            st.success('Verified')
            conn, c = db.connection()
            with conn:
                c.execute(
                    """
                    SELECT *
                    FROM department_record
                    WHERE id = %(id)s;
                    """,
                    {'id': id}
                )
                department_data = c.fetchall()
            st.write('Here are the details of the department you searched for:')
            show_department_details(department_data)
            conn.close()

    def list_dept_doctors(self):
        dept_id = st.text_input('Enter Department ID to get a list of doctors working in that department')
        if not dept_id:
            return
        elif not verify_department_id(dept_id):
            st.error('Invalid Department ID')
        else:
            st.success('Verified')
            conn, c = db.connection()
            with conn:
                c.execute(
                    """
                    SELECT id, name
                    FROM doctor_record
                    WHERE department_id = %(dept_id)s;
                    """,
                    {'dept_id': dept_id}
                )
                doctor_data = c.fetchall()
            st.write(f"Here is the list of doctors working in the {get_department_name(dept_id)} department:")
            show_list_of_doctors(doctor_data)
            conn.close()
