from flask import Flask
from flask_login import login_required , current_user


app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"