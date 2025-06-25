import os

dr_mls_access_code = 'access_auth'      # e.g. dr_mls_access_code = 'access_auth'

db_host = os.getenv("DB_HOST")
db_port = int(os.getenv("DB_PORT", 5432))
db_user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
db_database = os.getenv("DB_DATABASE")
edit_mode_password = 'allow_edit'
