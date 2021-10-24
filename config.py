import os

DEBUG = False
SQLALCHEMY_DATABASE_URI = os.environ.get('DB_VALID_URL', "sqlite:///data.db")

