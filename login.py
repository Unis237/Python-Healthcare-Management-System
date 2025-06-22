import streamlit as st
import psycopg2
import config
import hims_app  # Make sure hims_app.py is in the same directory

# Database connection
def get_db_connection():
    return psycopg2.connect(
        host=config.db_host,
        port=config.db_port,
        user=config.db_user,
        password=config.password,
        database=config.db_database
    )

# Validate user credentials
def validate_user(username, password):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT validate_user(%s::text, %s::text);", (username, password))
        result = cur.fetchone()
        return result[0] if result else False
    finally:
        cur.close()
        conn.close()

# Login form UI
def login():
    st.title("Login")

    username = st.text_input("Username", max_chars=50)
    password = st.text_input("Password", type="password", max_chars=50)

    if st.button("Submit"):
        if not username or not password:
            st.error("Please enter both username and password.")
            return

        if validate_user(username, password):
            st.session_state['logged_in'] = True
            st.session_state['username'] = username

            # Get user role from DB
            conn = get_db_connection()
            cur = conn.cursor()
            try:
                cur.execute("SELECT role FROM users WHERE username = %s;", (username,))
                role_result = cur.fetchone()
                st.session_state['role'] = role_result[0] if role_result else None
            finally:
                cur.close()
                conn.close()

            st.success("Login successful!")
            st.rerun()  # ✅ Use this instead of st.experimental_rerun()
        else:
            st.error("Invalid username or password.")

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['username'] = ''
    st.session_state['role'] = None

# Route to login or app
if st.session_state['logged_in']:
    hims_app.home()
else:
    login()
