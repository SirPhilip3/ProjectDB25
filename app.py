from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import login_required , current_user
from flask_sqlalchemy import SQLAlchemy 
from auth import auth
from database import db , app
from crud import *
from crud import book_ticket
from model import UserRole
from datetime import datetime, date

with app.app_context():
    db.create_all()

app.register_blueprint(auth, url_prefix='/auth')

@app.route("/", methods=['GET', 'POST'])
def hello_world():
    flights = []
    # se l'utente ha cliccato search in base.html
    if request.method == 'POST' :
        from_ = request.form.get('start_airport') 
        to_ = request.form.get('end_airport') 
        direct = request.form.get('direct_flight') == 'on' # True or False
        class_type = request.form.get('class_type', 'economy') # Economy, Business, First Class , economy è il default
        
        min_price = request.form.get('min_price')
        max_price = request.form.get('max_price') 
        sort_by = request.form.get('sort_by') 
        # funzione per cercare i voli , deve tornare una lista di voli con flight id
        flights = search_flight(from_, to_, direct, class_type, min_price, max_price, sort_by)
    return render_template("base.html", flights=flights, user=current_user)

# get information about the user (flights tikets etcc)
#! maybe inutile
@app.route("/user")
@login_required
def user():
    if current_user.role == UserRole.PASSENGER:
        tickets = get_user_tickets(current_user.id)
        return render_template('dashboard_user.html', user=current_user, tickets=tickets)
    else:
        return "<p>You are not authorized to view this page.</p>"

# information about the airline
@app.route("/airline")
@login_required
def airline_profile():
    #! maybe fare una funzione a parte per questo check
    if current_user.role == UserRole.AIRLINE:
        # mostra il profilo della compagnia aerea
        flights = get_flights_by_airline(current_user.airline_profile.id)
        return render_template('airline_profile.html', flights=flights)
    else:
        return "<p>You are not authorized to view this page.</p>"

# Per eliminare una tratta come compagnia aerea
@app.route("/delete_flight", methods=['POST'])
@login_required
def delete_flight():
    flight_id = request.form.get('flight_id')
    if current_user.role == UserRole.AIRLINE:
        delete_flight_by_id(flight_id)
        return redirect(url_for('airline_profile'))

@app.route("/add_flight", methods=['GET', 'POST'])
@login_required
def add_flight_page():
    if current_user.role == UserRole.AIRLINE:

        if request.method == 'POST':
            #! per ora gli aereoporti sono strighe
            departure_airport = request.form['from']
            arrival_airport = request.form['to']

            departure_time = request.form['departure_time']
            arrival_time = request.form['arrival_time']
            #! meglio usare un datetime picker per evitare errori di formato
            # To convert date and time strings to datetime objects, we can use the datetime module
            flight_date = date.today() 
            
            # Create datetime objects
            departure_time = datetime.combine(flight_date, datetime.strptime(departure_time, '%H:%M').time())
            arrival_time = datetime.combine(flight_date, datetime.strptime(arrival_time, '%H:%M').time())
            
            economy_price = float(request.form['price_economy'])
            business_price = float(request.form['price_business'])
            first_class_price = float(request.form['price_first'])

            airplane_id = request.form['airplane_id'] 
            #!! Importante: per ora non modello gli aereoporti attraverso la tabella ma solo con una stringa
            add_flight(current_user.airline_profile.id, airplane_id, departure_airport, arrival_airport, departure_time, arrival_time, economy_price, business_price, first_class_price)
    
        airplanes = get_airplanes_by_airline(current_user.airline_profile.id)
        
        return render_template('add_flight.html', airplanes=airplanes)
    else:
        return "<p>You are not authorized to view this page.</p>"
    
@app.route("/add_airplane", methods=['GET', 'POST'])
@login_required
def add_airplane_page():
    if current_user.role == UserRole.AIRLINE:
        if request.method == 'POST':
            model = request.form['model']
            capacity = int(request.form['capacity'])
            seats_economy = int(request.form['seats_economy'])
            seats_business = int(request.form['seats_business'])
            seats_first = int(request.form['seats_first'])
            # se è airline ha airline_profile e il suo id , altrimenti current_user.id è l'id dell'utente (cose diverse)
            add_airplane(model, capacity, seats_economy, seats_business, seats_first, current_user.airline_profile.id)
        return render_template('add_airplane.html')
    else:
        return "<p>You are not authorized to view this page.</p>"

# rotta per prenotare un biglietto 
@app.route("/flight/<int:flight_id>", methods=['GET', 'POST'])
@login_required
def flight_details(flight_id):
    # deve fare una query per prendere i dettagli del volo
    flight_details = get_flight_by_id(flight_id)
    message = None
    if current_user.role != UserRole.PASSENGER:
        flash('Only passengers can book tickets.', 'error')
        return redirect(url_for('hello_world'))

    if request.method == 'POST':
        flight_id = request.form.get('flight_id')
        ticket_class = request.form.get('ticket_class', 'economy')  # Default economy per ora 
        seat_number = request.form.get('seat_number')

        ticket , message = book_ticket(
            flight_id=flight_id,
            passenger_id=current_user.id,
            ticket_class=ticket_class,
            seat_number=seat_number
        )

        if ticket:
            flash('Ticket booked successfully!', 'success')
            # se ha successo ritorno alla pagina principale
            # o alla pagina in cui l'utente vede i suoi voli prenotati
            # per ora torno alla pagina principale
            return redirect(url_for('hello_world'))
        else:
            flash(f'Booking failed: {message}', 'error')
            return render_template('flight_details.html', flight_id=flight_id ,flight=flight_details, error=message)

    return render_template('flight_details.html', flight_id=flight_id ,flight=flight_details, error=message)

#tickets route 
# @app.route('/tickets', methods=['GET', 'POST'])
# @login_required
# def tickets():
