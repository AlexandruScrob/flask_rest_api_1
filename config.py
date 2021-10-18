import os

DEBUG = False
DATABASE_URI = os.environ.get('DB_VALID_URL', "sqlite:///data.db")

