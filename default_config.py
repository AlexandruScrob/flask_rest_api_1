import os
from datetime import timedelta

DEBUG = True
DATABASE_URI = "sqlite:///data.db"
SQLALCHEMY_TRACK_MODIFICATIONS = False
PROPAGATE_EXCEPTIONS = True
JWT_EXPIRATION_DELTA = timedelta(seconds=1800)
APP_SECRET_KEY = os.environ['APP_SECRET_KEY']
