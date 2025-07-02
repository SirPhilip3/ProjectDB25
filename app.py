from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import login_required , current_user
from flask_sqlalchemy import SQLAlchemy 
from auth import auth
from database import db , app
from crud import *

with app.app_context():
    db.create_all()

app.register_blueprint(auth, url_prefix='/auth')

@app.route("/", methods=['GET', 'POST'])
def hello_world():
    flights = []
    # se l'utente ha cliccato search in base.html
    if request.method == 'POST' and 'search' in request.form:
        from_ = request.form.get('start_airport') 
        to_ = request.form.get('end_airport') 
        direct = request.form.get('direct_flight') # True or False
        class_type = request.form.get('class_type') # Economy, Business, First Class
        # funzione per cercare i voli , deve tornare una lista di voli con flight id
        flights = search_flight(from_, to_, direct, class_type)
    return render_template("base.html", flights=flights)

# get information about the user (flights tikets etcc)
#! maybe inutile
@app.route("/user")
@login_required
def user():
    if current_user.is_authenticated:
        return f"<p>Welcome, {current_user.username}! {current_user.role}</p>"
    else:
        return "<p>You are not logged in.</p>"

@app.route("/flight/<int:flight_id>")
def flight_details(flight_id):
    # deve fare una query per prendere i dettagli del volo
    flight_details = get_flight_by_id(flight_id)

    if request.method == 'POST':
        if current_user.is_authenticated :
            # aggiungi il ticket al database
            book_ticket()
        else :
            flash("You must be logged in to book a flight.")
            return redirect(url_for('login'))
    
    return render_template('flight_details.html', flight=flight_details)

# information about the airline
@app.route("/airline")
@login_required
def airline_profile():
    #! maybe fare una funzione a parte per questo check
    if current_user.role == 'airline':
        # mostra il profilo della compagnia aerea
        return render_template('airline_profile.html')
    else:
        return "<p>You are not authorized to view this page.</p>"

@app.route("/add_flight", methods=['GET', 'POST'])
@login_required
def add_flight():
    if current_user.role == 'airline':
      return render_template('add_flight.html')
    else:
        return "<p>You are not authorized to view this page.</p>"
    
@app.route("/add_airplane", methods=['GET', 'POST'])
@login_required
def add_airplane():
    if current_user.role == 'airline':
      return render_template('add_airplane.html')
    else:
        return "<p>You are not authorized to view this page.</p>"