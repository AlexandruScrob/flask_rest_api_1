import os
from datetime import timedelta

DEBUG = True
# SQLALCHEMY_DATABASE_URI = "sqlite:///data.db"
SQLALCHEMY_DATABASE_URI = "postgresql://sjwvvwnj:SXjNNGDAaC3LUhBPpMqLT" \
                          "ZtTGRTNQaP-@tai.db.elephantsql.com/sjwvvwnj"
SQLALCHEMY_TRACK_MODIFICATIONS = False
PROPAGATE_EXCEPTIONS = True
JWT_EXPIRATION_DELTA = timedelta(seconds=1800)
APP_SECRET_KEY = os.environ['APP_SECRET_KEY']
UPLOADED_IMAGES_DEST = os.path.join("static", "images")
JWT_AUTH_USERNAME_KEY = 'email'
