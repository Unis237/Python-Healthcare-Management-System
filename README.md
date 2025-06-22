# Python Healthcare Management System

## Setup and Installation Guide

Follow these steps to clone and set up the project on your local machine:

### 1. Clone the Repository
```bash
git clone <repository-url>
cd python-healthcare-management
```

### 2. Set Up PostgreSQL Database
- Ensure you have PostgreSQL installed and running.
- Create a new database named `health` (or your preferred name).
```sql
CREATE DATABASE health;
```
- Make sure the `pgcrypto` extension is enabled in your database for password hashing:
```sql you can checck the insert.sql file
CREATE EXTENSION IF NOT EXISTS pgcrypto;
```

### 3. Configure Database Credentials
- Open the `config.py` file.
- Update the database connection parameters (`db_host`, `db_port`, `db_user`, `password`, `db_database`) to match your PostgreSQL setup.

### 4. Set Up Python Environment
- It is recommended to use a virtual environment.
```bash
python -m venv venv
venv\Scripts\activate   # On Windows
# or
source venv/bin/activate  # On macOS/Linux
```
- Install required Python packages:
```bash
pip install -r requirements.txt
```
If `requirements.txt` is not present, install manually:
```bash
pip install streamlit psycopg2
```

### 5. Initialize the Database Schema
- Run the database initialization script to create tables and functions:
```bash
python init_db.py
```

### 6. Run the Application
- Start the Streamlit login page:
```bash
streamlit run login.py
```
- Use the login page to enter your credentials and access the main application.

## Notes
- Password hashing and validation are handled securely in the PostgreSQL database using the `pgcrypto` extension.
- The login page is implemented using Streamlit and integrates with the database for authentication.
- The main application interface is in `hims_app.py`, which loads after successful login.

## Troubleshooting
- Ensure PostgreSQL is running and accessible.
- Verify database credentials in `config.py`.
- Confirm the `pgcrypto` extension is enabled in your database.
- If you encounter issues with package installation, ensure your Python environment is activated.

## Contact
For any issues or questions, please contact the project maintainers Abia, Kong or Loyck.
