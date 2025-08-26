from flask_login import *
from werkzeug.security import check_password_hash, generate_password_hash
from flask import Flask, render_template, request, redirect, url_for, flash , Blueprint
from database import db, app 
from model import User, UserRole, Airline
import uuid
from crud import decode_sql_errors

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
        email = request.form['email']
        password = request.form['password']
        #? first da riguardare
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')
            if user.role == UserRole.AIRLINE:
                return redirect(url_for('airline_profile', airline_id=user.id))
            elif user.role == UserRole.PASSENGER:
                #! Fix qunado cerci un volo e non sei loggato crasha
                #! se sei airline non dovresti poter cliccare select flight
                #? redirect to user profile or base (dove ci sono i voli)
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                # url = request.referrer
                # if 'flight' in url: # se arriva richiest da flight_details dopo aver fatto login ritorna alla pagina del volo che si stava visualizzando
                #     # idealmente dovrebbe rimanere nello stato in cui si trovava prima del login
                #     return redirect(url_for('flight_details', flight_id=request.args.get('flight')))
                return redirect(url_for('hello_world')) # ritorna alla lista dei voli (potremmo far tornare a pagina specifica dello user)
        else:
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
    return render_template("/auth/login.html")

# diverisfy for role
@app.route("/register" , methods=['GET', 'POST'])
def register ():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        address = request.form.get('address')

        type = request.form.get('role')
        role = UserRole.AIRLINE if type == 'true' else UserRole.PASSENGER

        # Se l'utente è un airline richiedi il nome della compagnia aerea, altrimenti nome e cognome
        airline_name = request.form.get('airline_name') if role == UserRole.AIRLINE else None
        firstname = request.form.get('firstname') if role == UserRole.PASSENGER else None
        lastname = request.form.get('lastname') if role == UserRole.PASSENGER else None

        # Controlla se email è già usata
        if User.query.filter_by(email=email).first():
            flash('This email is already registered.', 'danger')
            return redirect(url_for('register'))

        # Controlla se airline name esiste già
        if role == UserRole.AIRLINE and Airline.query.filter_by(name=airline_name).first():
            flash('Airline name already exists.', 'danger')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(email=email, role=role, password=hashed_password, phone=phone, address=address, firstname=firstname, lastname=lastname)
        try :
            db.session.add(new_user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            error_msg = decode_sql_errors(e)
            flash(f"Error creating user: {error_msg}", 'danger')
            print(f"Error occurred: {e}")

        if role == UserRole.AIRLINE:
            if not airline_name:
                flash('Airline Name is required for Airline role.', 'danger')
                return redirect(url_for('register'))
            if Airline.query.filter_by(name=airline_name).first():
                flash('Airline name already exists.', 'danger')
                return redirect(url_for('register'))
            
            new_airline = Airline(name=airline_name, user_id=new_user.id)
            new_user.airline_profile = new_airline
            try :
                db.session.add(new_airline)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                error_msg = decode_sql_errors(e)
                flash(f"Error creating airline profile: {error_msg}", 'danger')
                print(f"Error occurred: {e}")

        flash('Registration successful! Please log in.', 'success')

        return redirect(url_for('login'))
    
    return render_template("/auth/register.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('hello_world'))








