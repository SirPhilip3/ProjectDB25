from flask_login import *
from werkzeug.security import check_password_hash, generate_password_hash
from flask import Flask, render_template, request, redirect, url_for, flash , Blueprint
from database import db, app 
from model import User
import uuid

auth = Blueprint('auth', __name__)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route ("/login" , methods=['GET', 'POST'])
def login ():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!')
            return redirect(url_for('feed'))
        else:
            flash('Invalid username or password')
            return redirect(url_for('login'))
    return render_template("/auth/login.html")

@app.route("/register" , methods=['GET', 'POST'])
def register ():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template("/auth/register.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    # flash('Logged out successfully.')
    return redirect(url_for('hello_world'))
