from flask import Flask, render_template, request, redirect, url_for, flash, make_response
from flask_login import login_required , current_user
from flask_sqlalchemy import SQLAlchemy 
from auth import auth
from database import db , app
from crud import *
from model import UserRole
from datetime import datetime, date

from socket_ import *
from socket_io_init import socketio

with app.app_context():
    db.create_all()
    carica_triggers()

app.register_blueprint(auth, url_prefix='/auth')

# 404 page
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html')

@app.route("/", methods=['GET', 'POST'])
def hello_world():
    flights = []
    direct = False # False di default

    search = False # Variabile per non mostrare "No flights available for the selected route." al primo caricamento della pagina

    form_data = {}

    if request.method == 'POST':
        if 'reset' in request.form:
            # Reset: nessun filtro, nessun volo, nessun search
            return render_template("base.html", flights=[], user=current_user, direct_flight=False, search=False, cached_form={})
        
        from_ = request.form.get('start_airport') 
        to_ = request.form.get('end_airport') 

        direct = request.form.get('direct_flight') == 'on' # True or False

        class_type = request.form.get('flight_class') # Economy, Business, First Class 
        
        departure_date_str = request.form.get('departure_date')
        if departure_date_str:
            departure_date = datetime.fromisoformat(departure_date_str)
        else: 
            departure_date = datetime.now()
            departure_date_str = departure_date.isoformat(timespec='minutes')  # formato compatibile con input type="datetime-local"


        # per far specificare all'utente l'orario massimo di arrivo
        arrival_date = request.form.get('arrival_date')

        min_price = request.form.get('min_price')
        max_price = request.form.get('max_price') 
        sort_by = request.form.get('sort_by') 

        form_data = {
            "from": from_,
            "to": to_,
            "direct": direct,
            "departure_date": departure_date_str,
            "arrival_date": arrival_date,
            "min_price": min_price,
            "max_price": max_price,
            "sort_by": sort_by
        }
        print(form_data)

        search = True
        # funzione per cercare i voli
        flights = search_flight(from_, to_, direct, min_price, max_price, sort_by, departure_date, arrival_date)
    return render_template("base.html", flights=flights, user=current_user, direct_flight=direct, search=search, cached_form=form_data)

# Recuper le informazioni dell'utente (flights tikets etc.)
@app.route("/user")
@login_required
def user():
    if current_user.role == UserRole.PASSENGER:
        tickets = get_user_tickets(current_user.id)
        # Elimina la cache
        response = make_response(render_template('dashboard_user.html', user=current_user, tickets=tickets))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response
    else:
        return render_template('unauthorized.html')

# informazioni riguardanti la compagnia aerea
@app.route("/airline/<uuid:airline_id>")
@login_required
def airline_profile(airline_id):
    if current_user.role == UserRole.AIRLINE:
        # mostra il profilo della compagnia aerea
        airline_info = get_airline_info(current_user.airline_profile.id)

        flights = get_flights_by_airline(current_user.airline_profile.id)
        airplanes = get_airplanes_by_airline(current_user.airline_profile.id)

        n_flights , n_airplanes, n_tickets , tot_revenue = get_airline_statistics(current_user.airline_profile.id)

        top_routes = get_airline_top_routes(current_user.airline_profile.id)
        class_distribution = get_airline_class_distribution(current_user.airline_profile.id)

        response = make_response(render_template('airline_profile.html', airline_info=airline_info, flights=flights, airplanes=airplanes, class_distribution=class_distribution, top_routes=top_routes, n_flights=n_flights, n_airplanes=n_airplanes, n_tickets=n_tickets, tot_revenue=tot_revenue))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        
        return response
    else:
        render_template('unauthorized.html')

# Per eliminare una tratta come compagnia aerea
@app.route("/delete_flight", methods=['POST'])
@login_required
def delete_flight():
    flight_id = request.form.get('flight_id')
    if current_user.role == UserRole.AIRLINE:
        delete_flight_by_id(flight_id)
        return redirect(url_for('airline_profile', airline_id=current_user.airline_profile.id))

# Per eliminare un aereo come compagnia aerea
@app.route("/delete_airplane", methods=['POST'])
@login_required
def delete_airplane():
    airplane_id = request.form.get('airplane_id')
    if current_user.role == UserRole.AIRLINE:
        delete_airplane_by_id(airplane_id)
        return redirect(url_for('airline_profile', airline_id=current_user.airline_profile.id))

# Per eliminare un ticket come passeggero
@app.route("/delete_ticket", methods=['POST'])
@login_required
def delete_ticket():
    ticket_id = request.form.get('ticket_id')
    if current_user.role == UserRole.PASSENGER:
        delete_ticket_by_id(ticket_id)
        return redirect(url_for('user', user_id=current_user.id))

# Per aggiungere una tratta come compagnia aerea
@app.route("/add_flight", methods=['GET', 'POST'])
@login_required
def add_flight_page():
    if current_user.role == UserRole.AIRLINE:

        if request.method == 'POST':
            departure_airport = request.form['from']
            arrival_airport = request.form['to']
            
            departure_time = datetime.fromisoformat(request.form['departure_time'])
            arrival_time = datetime.fromisoformat(request.form['arrival_time'])
            
            economy_price = float(request.form['price_economy'])
            business_price = float(request.form['price_business'])
            first_class_price = float(request.form['price_first'])

            airplane_id = request.form['airplane_id'] 
            
            extras = []
            for key, value in request.form.items():
                if key.startswith('extra_name') and value:
                    number = key.split('_')[-1]
                    price = request.form.get(f'extra_price_{number}')
                    if price:
                        extras.append({
                            'name': value,
                            'price': float(price) 
                        })
                    else :
                        print(f"Extra {value} has no price, skipping.")
            try :
                new_flight = add_flight(current_user.airline_profile.id, airplane_id, departure_airport, arrival_airport, departure_time, arrival_time, economy_price, business_price, first_class_price, extras)
                if new_flight:
                    flash("Flight added successfully.", "success")
            except Exception as e:
                flash(f"Error: {e}", "danger")

        airplanes = get_airplanes_by_airline(current_user.airline_profile.id)

        return render_template('add_flight.html', airplanes=airplanes)
    else:
        return render_template('unauthorized.html')

# Per aggiungere un aereo come compagnia aerea
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
            # se è airline ha airline_profile e il suo id , altrimenti current_user.id è l'id dell'utente 
            add_airplane(model, capacity, seats_economy, seats_business, seats_first, current_user.airline_profile.id)
        return render_template('add_airplane.html')
    else:
        return render_template('unauthorized.html')

# Per prenotare un biglietto 
@app.route("/flight/<uuid:flight_id>", methods=['GET', 'POST'])
@login_required
def flight_details(flight_id):
    # query per prendere i dettagli del volo
    flight_details = get_flight_by_id(str(flight_id))
    message = None

    if current_user.role != UserRole.PASSENGER:
        flash('Only passengers can book tickets.', 'danger')
        return redirect(url_for('hello_world'))

    available_tickets = get_remaining_ticket_count_by_flight(flight_id)
    occupied_seats = get_occupied_seats(flight_id)
    if request.method == 'POST':
        flight_id = request.form.get('flight_id')
        seat_number = request.form.get('seat_number')

        seat_letter = seat_number[0]
        if seat_letter == 'E':
            ticket_class = 'economy'
        elif seat_letter == 'B':
            ticket_class = 'business'
        elif seat_letter == 'F':
            ticket_class = 'first_class'
        else:
            message = "Invalid seat number format."

        print(f"Attempting to book ticket: {flight_id}, {seat_number}")

        selected_extras = []
        for value in request.form.getlist('selected_extras[]'):
            if value:
                name , cost = value.split('|')
                if name and cost:
                    selected_extras.append({
                        'name': name,
                        'price': float(cost)
                    })
                else :
                    print("Invalid extra selected")

        ticket = book_ticket(
            flight_id=flight_id,
            passenger_id=current_user.id,
            ticket_class=ticket_class,
            seat_number=seat_number,
            selected_extras=selected_extras
        )

        if ticket:
            flash('Ticket booked successfully!', 'success')
            return redirect(url_for('hello_world'))
        else:
            print(f'Booking failed: {message}')
            return render_template('flight_details.html', flight_id=flight_id ,flight=flight_details, available_tickets=available_tickets, seat_status=occupied_seats)

    return render_template('flight_details.html', flight_id=flight_id ,flight=flight_details, available_tickets=available_tickets, seat_status=occupied_seats)


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)