from flask import Flask, render_template, request, redirect, url_for, flash, make_response
from flask_login import login_required , current_user
from flask_sqlalchemy import SQLAlchemy 
from auth import auth
from database import db , app
from crud import *
from model import UserRole
from datetime import datetime, date

from socket_test import *
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
    #! potremmo fare che l'utente non deve selezionare direct o non e facciamo vedere i due risultati assieme
    direct = False # False di default
    # se l'utente ha cliccato search in base.html
    if request.method == 'POST':
        #! ricerca aereoporti non usata
        # departure_airport_name = request.form['name_from']
        # departure_airport_city = request.form['city_from']
        # departure_airport_iata = request.form['iata_from']

        # arrival_airport_name = request.form['name_to']
        # arrival_airport_city = request.form['city_to']
        # arrival_airport_iata = request.form['iata_to']

        # departure_airport = search_airport(departure_airport_name, departure_airport_city, departure_airport_iata)
        # arrival_airport = search_airport(arrival_airport_name, arrival_airport_city, arrival_airport_iata)
        # 
        # if not departure_airport or not arrival_airport:
        #     print("One or both airports not found, please check the input.")
        #     redirect(url_for('hello_world'))
        
        from_ = request.form.get('start_airport') 
        to_ = request.form.get('end_airport') 
        direct = request.form.get('direct_flight') == 'on' # True or False
        class_type = request.form.get('flight_class') # Economy, Business, First Class 
        
        min_price = request.form.get('min_price')
        max_price = request.form.get('max_price') 
        sort_by = request.form.get('sort_by') 
        
        # funzione per cercare i voli , deve tornare una lista di voli con flight id
        flights = search_flight(from_, to_, direct, class_type, min_price, max_price, sort_by)
    return render_template("base.html", flights=flights, user=current_user, direct_flight=direct)

# get information about the user (flights tikets etcc)
#! maybe inutile
@app.route("/user")
@login_required
def user():
    if current_user.role == UserRole.PASSENGER:
        tickets = get_user_tickets(current_user.id)
        # remove cache
        response = make_response(render_template('dashboard_user.html', user=current_user, tickets=tickets))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response
    else:
        return "<p>You are not authorized to view this page.</p>"

# information about the airline
#! protrei entrare quando faccio back 
@app.route("/airline/<uuid:airline_id>")
@login_required
def airline_profile(airline_id):
    #! maybe fare una funzione a parte per questo check
    if current_user.role == UserRole.AIRLINE:
        # mostra il profilo della compagnia aerea
        flights = get_flights_by_airline(current_user.airline_profile.id)
        airplanes = get_airplanes_by_airline(current_user.airline_profile.id)

        # DEGUB
        n_flights , n_airplanes, n_tickets , tot_revenue = get_airline_statistics(current_user.airline_profile.id)
        print(f"Airline {current_user.airline_profile.id} has {n_flights} flights, {n_airplanes} airplanes, {n_tickets} tickets sold, total revenue: {tot_revenue}")


        top_routes = get_airline_top_routes(current_user.airline_profile.id)
        class_distribution = get_airline_class_distribution(current_user.airline_profile.id)


        



        # Per risolvere il fatto che cliccando indietro posso tornare su una pagina che necessita di login 
        # quando clicca indietro il broswer non fa una nuova richiesta ma mostra la pagina cache
        # aggiunge headers per disabilitare la cache
        response = make_response(render_template('airline_profile.html', flights=flights, airplanes=airplanes ,     class_distribution=class_distribution,top_routes=top_routes))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        
        return response
    else:
        return "<p>You are not authorized to view this page.</p>"

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

# Per eliminare un aereo come compagnia aerea
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
            #! se volessimo usare la tabella ereoporti
            # departure_airport_name = request.form['name_from']
            # departure_airport_city = request.form['city_from']
            # departure_airport_iata = request.form['iata_from']

            # arrival_airport_name = request.form['name_to']
            # arrival_airport_city = request.form['city_to']
            # arrival_airport_iata = request.form['iata_to']
        
            # departure_airport = search_airport(departure_airport_name, departure_airport_city, departure_airport_iata)
            # if not departure_airport :
            #     print("Departure airport not found, adding it.")
            #     departure_airport=add_airport(departure_airport_name, departure_airport_city, departure_airport_iata)
            
            # arrival_airport = search_airport(arrival_airport_name, arrival_airport_city, arrival_airport_iata)
            # if not arrival_airport :
            #     print("Departure airport not found, adding it.")
            #     arrival_airport=add_airport(arrival_airport_name, arrival_airport_city, arrival_airport_iata)

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
            
            add_flight(current_user.airline_profile.id, airplane_id, departure_airport, arrival_airport, departure_time, arrival_time, economy_price, business_price, first_class_price, extras)
    
        airplanes = get_airplanes_by_airline(current_user.airline_profile.id)
        
        return render_template('add_flight.html', airplanes=airplanes)
    else:
        return "<p>You are not authorized to view this page.</p>"

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
            # se è airline ha airline_profile e il suo id , altrimenti current_user.id è l'id dell'utente (cose diverse)
            add_airplane(model, capacity, seats_economy, seats_business, seats_first, current_user.airline_profile.id)
        return render_template('add_airplane.html')
    else:
        return "<p>You are not authorized to view this page.</p>"

# Per prenotare un biglietto 
@app.route("/flight/<uuid:flight_id>", methods=['GET', 'POST'])
@login_required
def flight_details(flight_id):
    # deve fare una query per prendere i dettagli del volo
    flight_details = get_flight_by_id(str(flight_id))
    message = None

    if current_user.role != UserRole.PASSENGER:
        flash('Only passengers can book tickets.', 'error')
        return redirect(url_for('hello_world'))

    available_tickets = get_remaining_ticket_count_by_flight(flight_id)

    if request.method == 'POST':
        flight_id = request.form.get('flight_id')
        ticket_class = request.form.get('flight_class')  
        seat_number = request.form.get('seat_number')

        selected_extras = []
        for key, value in request.form.items():
            if key == "selected_extras" and value:
                name , cost = value.split('|')
                if name and cost:
                    selected_extras.append({
                        'name': name,
                        'price': float(cost)
                    })
                else :
                    print("Invalid extra selected")

        ticket , message = book_ticket(
            flight_id=flight_id,
            passenger_id=current_user.id,
            ticket_class=ticket_class,
            seat_number=seat_number,
            selected_extras=selected_extras
        )

        if ticket:
            flash('Ticket booked successfully!', 'success')
            # se ha successo ritorno alla pagina principale
            # o alla pagina in cui l'utente vede i suoi voli prenotati
            # per ora torno alla pagina principale
            return redirect(url_for('hello_world'))
        else:
            flash(f'Booking failed: {message}', 'error')
            return render_template('flight_details.html', flight_id=flight_id ,flight=flight_details, error=message, available_tickets=available_tickets)

    return render_template('flight_details.html', flight_id=flight_id ,flight=flight_details, error=message, available_tickets=available_tickets)



if __name__ == '__main__':
    # Use socketio.run() instead of app.run() to enable Socket.IO
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)