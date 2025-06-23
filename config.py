import os

dr_mls_access_code = 'access_auth'      # e.g. dr_mls_access_code = 'access_auth'

# PostgreSQL connection parameters from environment variables with fallback defaults
db_host = os.environ.get('DB_HOST', 'localhost')                           # e.g. 'localhost'
db_port = int(os.environ.get('DB_PORT', 5432))                            # default PostgreSQL port
db_user = os.environ.get('DB_USER', 'postgres')                          # e.g. 'postgres'
password = os.environ.get('DB_PASSWORD', '1234')                         # e.g. password = '1234'
db_database = os.environ.get('DB_DATABASE', 'healthcare_db')             # e.g. 'healthcare_db'

edit_mode_password = 'allow_edit'
