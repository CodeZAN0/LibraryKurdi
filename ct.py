from app import db, app
from flask_migrate import Migrate



# Create the tables
with app.app_context():
    db.create_all()
    print("Tables created successfully.")
