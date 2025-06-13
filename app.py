from flask import Flask
from flask_login import login_required , current_user
from flask_sqlalchemy import SQLAlchemy 
from auth import auth
from database import db , app

with app.app_context():
    db.create_all()

app.register_blueprint(auth, url_prefix='/auth')

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/user")
@login_required
def user():
    if current_user.is_authenticated:
        return f"<p>Welcome, {current_user.username}!</p>"
    else:
        return "<p>You are not logged in.</p>"