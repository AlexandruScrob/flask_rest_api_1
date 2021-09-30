from app import app
from db import db

db.init_app(app)


# TODO creates tables that it sees (from imports)
@app.before_first_request
def create_tables():
    db.create_all()
