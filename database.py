from flask_sqlalchemy import SQLAlchemy 
from flask import Flask

app = Flask(__name__)

# PostgreSQL database connection change with your credentials
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://postgres:1234@localhost:5432/Project-DB-test"
app.secret_key = 'your_secret_key'  # Replace with your actual secret key

db = SQLAlchemy(app)