import streamlit as st
import database as db
from patient import Patient
from department import Department
from doctor import Doctor
from prescription import Prescription
from medical_test import Medical_Test
import config
import psycopg2 as sql

# Initialize session state keys safely
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ''
if 'role' not in st.session_state:
    st.session_state['role'] = None

# Database connection helper
def connection():
    conn = psycopg2.connect(
        host=config.db_host,
        port=config.db_port,
        user=config.db_user,
        password=config.password,
        database=config.db_database
    )
    c = conn.cursor()
    return conn, c

# Patients module UI
def patients(role):
    st.header('PATIENTS')
    p = Patient()
    option_list = ['', 'Show complete patient record', 'Search patient'] if role == 'doctor' else ['', 'Add patient', 'Update patient', 'Delete patient', 'Show complete patient record', 'Search patient']
    option = st.sidebar.selectbox('Select function', option_list)

    if role != 'doctor' and option == 'Add patient':
        st.subheader('ADD PATIENT')
        p.add_patient()
    elif role != 'doctor' and option == 'Update patient':
        st.subheader('UPDATE PATIENT')
        p.update_patient()
    elif role != 'doctor' and option == 'Delete patient':
        st.subheader('DELETE PATIENT')
        try:
            p.delete_patient()
        except sql.IntegrityError:
            st.error('This entry cannot be deleted as other records are using it.')
    elif option == 'Show complete patient record':
        st.subheader('COMPLETE PATIENT RECORD')
        p.show_all_patients()
    elif option == 'Search patient':
        st.subheader('SEARCH PATIENT')
        p.search_patient()

# Doctors module UI
def doctors(role):
    if role == 'doctor':
        return  # Hide doctors module from doctors
    st.header('DOCTORS')
    dr = Doctor()
    option_list = ['', 'Add doctor', 'Update doctor', 'Delete doctor', 'Show complete doctor record', 'Search doctor']
    option = st.sidebar.selectbox('Select function', option_list)

    if option == 'Add doctor':
        st.subheader('ADD DOCTOR')
        dr.add_doctor()
    elif option == 'Update doctor':
        st.subheader('UPDATE DOCTOR')
        dr.update_doctor()
    elif option == 'Delete doctor':
        st.subheader('DELETE DOCTOR')
        try:
            dr.delete_doctor()
        except sql.IntegrityError:
            st.error('This entry cannot be deleted as other records are using it.')
    elif option == 'Show complete doctor record':
        st.subheader('COMPLETE DOCTOR RECORD')
        dr.show_all_doctors()
    elif option == 'Search doctor':
        st.subheader('SEARCH DOCTOR')
        dr.search_doctor()

# Prescriptions module UI
def prescriptions(role):
    st.header('PRESCRIPTIONS')
    m = Prescription()
    option_list = ['', 'Add prescription', 'Update prescription', 'Delete prescription', 'Show prescriptions of a particular patient'] if role == 'doctor' else ['', 'Show prescriptions of a particular patient']
    option = st.sidebar.selectbox('Select function', option_list)

    if role == 'doctor' and option == 'Add prescription':
        st.subheader('ADD PRESCRIPTION')
        m.add_prescription()
    elif role == 'doctor' and option == 'Update prescription':
        st.subheader('UPDATE PRESCRIPTION')
        m.update_prescription()
    elif role == 'doctor' and option == 'Delete prescription':
        st.subheader('DELETE PRESCRIPTION')
        m.delete_prescription()
    elif option == 'Show prescriptions of a particular patient':
        st.subheader('PRESCRIPTIONS OF A PARTICULAR PATIENT')
        m.prescriptions_by_patient()

# Medical tests module UI
def medical_tests(role):
    st.header('MEDICAL TESTS')
    t = Medical_Test()
    option_list = ['', 'Add medical test', 'Update medical test', 'Delete medical test', 'Show medical tests of a particular patient'] if role == 'doctor' else ['', 'Show medical tests of a particular patient']
    option = st.sidebar.selectbox('Select function', option_list)

    if role == 'doctor' and option == 'Add medical test':
        st.subheader('ADD MEDICAL TEST')
        t.add_medical_test()
    elif role == 'doctor' and option == 'Update medical test':
        st.subheader('UPDATE MEDICAL TEST')
        t.update_medical_test()
    elif role == 'doctor' and option == 'Delete medical test':
        st.subheader('DELETE MEDICAL TEST')
        t.delete_medical_test()
    elif option == 'Show medical tests of a particular patient':
        st.subheader('MEDICAL TESTS OF A PARTICULAR PATIENT')
        t.medical_tests_by_patient()

# Departments module UI
def departments(role):
    st.header('DEPARTMENTS')
    d = Department()
    option_list = (
        ['', 'Show complete department record', 'Search department', 'Show doctors of a particular department']
        if role == 'doctor'
        else ['', 'Add department', 'Update department', 'Delete department', 'Show complete department record', 'Search department', 'Show doctors of a particular department']
    )
    option = st.sidebar.selectbox('Select function', option_list)

    if role != 'doctor' and option == 'Add department':
        st.subheader('ADD DEPARTMENT')
        d.add_department()
    elif role != 'doctor' and option == 'Update department':
        st.subheader('UPDATE DEPARTMENT')
        d.update_department()
    elif role != 'doctor' and option == 'Delete department':
        st.subheader('DELETE DEPARTMENT')
        try:
            d.delete_department()
        except sql.IntegrityError:
            st.error('This entry cannot be deleted as other records are using it.')
    elif option == 'Show complete department record':
        st.subheader('COMPLETE DEPARTMENT RECORD')
        d.show_all_departments()
    elif option == 'Search department':
        st.subheader('SEARCH DEPARTMENT')
        d.search_department()
    elif option == 'Show doctors of a particular department':
        st.subheader('DOCTORS OF A PARTICULAR DEPARTMENT')
        d.list_dept_doctors()

# Main home page
def home():
    db.db_init()  # Initialize DB and tables if needed
    role = st.session_state.get('role', None)

    if role is None:
        st.error("User role not found, please login again.")
        st.session_state['logged_in'] = False
        st.session_state['username'] = ''
        st.session_state['role'] = None
        st.rerun()
        return

    st.sidebar.title("Main Menu")
    option = st.sidebar.selectbox('Select module', ['', 'Patients', 'Doctors', 'Prescriptions', 'Medical Tests', 'Departments'])

    if option == 'Patients':
        patients(role)
    elif option == 'Doctors':
        doctors(role)
    elif option == 'Prescriptions':
        prescriptions(role)
    elif option == 'Medical Tests':
        medical_tests(role)
    elif option == 'Departments':
        departments(role)

    if st.sidebar.button('Logout'):
        st.session_state['logged_in'] = False
        st.session_state['username'] = ''
        st.session_state['role'] = None
        st.success("You have been logged out.")
        st.rerun()
        

# Run home page if logged in, otherwise do nothing (login.py handles login)
if st.session_state['logged_in']:
    home()
