# crud operations for the database
from database import db
from model import User , Flight, Airplane, Airline, Ticket
from sqlalchemy.orm import aliased 
from sqlalchemy import text
from flask import flash, redirect, url_for
from datetime import timedelta

def carica_triggers():
    with open('triggers.sql', 'r') as file:
        sql_script = file.read()
        with db.engine.begin() as connection:
            for statement in sql_script.split('#'):
                stmt = statement.strip()
                if stmt:
                    connection.execute(text(stmt))

# Aggiunge una tratta al database
def add_flight(airline_id, airplane_id, departure_airport, arrival_airport ,departure_time, arrival_time, economy_price, business_price, first_class_price):
    new_flight = Flight(
        airline_id=airline_id,
        airplane_id=airplane_id,
        departure_airport=departure_airport,
        destination_airport=arrival_airport,
        departure_time=departure_time,
        arrival_time=arrival_time,
        economy_price=economy_price,
        business_price=business_price,
        first_class_price=first_class_price
    )
    try:
        db.session.add(new_flight)
        db.session.commit()
    except Exception as e:
        flash(str(e))
        return redirect(url_for('add_flight_page'))

# Aggiunge un aereoplano al database
def add_airplane(model, capacity, economy_seats, business_seats, first_class_seats, airline_id):
    new_airplane = Airplane(
        model=model,
        capacity=capacity,
        economy_seats=economy_seats,
        business_seats=business_seats,
        first_class_seats=first_class_seats,
        airline_id=airline_id
    )
    db.session.add(new_airplane)
    db.session.commit()

def delete_flight_by_id(flight_id):
    flight = Flight.query.get(flight_id)
    if flight:
        db.session.delete(flight)
        db.session.commit()

# Ritorna i voli diretti o indiretti filtrati con i parametri corrispondenti
#! da rivedere l'implemetazione
def search_flight(departure, arrival, direct_flight, class_type, min_price=None, max_price=None, sort_by=None):
    if direct_flight:
        query = Flight.query.filter(
            Flight.departure_airport == departure, 
            Flight.destination_airport == arrival)
    else:
        F1 = aliased(Flight)
        F2 = aliased(Flight)
        query = db.session.query(F1, F2).filter(
            F1.departure_airport == departure,
            F1.destination_airport == F2.departure_airport,
            F2.destination_airport == arrival,
            # devono essere separati da almeno 2 ore , potremmo aggiungere un limite massimo
            F2.departure_time >= F1.arrival_time + timedelta(hours=2))
    
    # Filtri per prezzo
    #! implementazione diversa per i voli con uno stop 
    if min_price:
        min_price = float(min_price)
        price_field = getattr(Flight, f"{class_type}_price")
        query = query.filter(price_field >= min_price)
    
    if max_price:
        max_price = float(max_price)
        price_field = getattr(Flight, f"{class_type}_price")
        query = query.filter(price_field <= max_price)
    
    # Ordinamento
    if sort_by:
        if sort_by == 'price_asc':
            price_field = getattr(Flight, f"{class_type}_price")
            query = query.order_by(price_field.asc())
        elif sort_by == 'price_desc':
            price_field = getattr(Flight, f"{class_type}_price")
            query = query.order_by(price_field.desc())
        elif sort_by == 'departure_asc':
            query = query.order_by(Flight.departure_time.asc())
        elif sort_by == 'departure_desc':
            query = query.order_by(Flight.departure_time.desc())
        elif sort_by == 'duration_asc':
            query = query.order_by((Flight.arrival_time - Flight.departure_time).asc())
    
    # Esegui la query
    flights = query.all()
    
    #! implementazione diversa per i voli con uno stop 
    if direct_flight:
        # aggiunge 2 campi temporanei per il tipo di classe e il prezzo selezionato
        for flight in flights:
            flight.selected_class = class_type
            flight.selected_price = getattr(flight, f"{class_type}_price")
    else:
        # aggiunge 2 campi temporanei per il tipo di classe e il prezzo selezionato
        for first_flight, second_flight in flights:
            first_flight.selected_class = class_type
            first_flight.selected_price = getattr(first_flight, f"{class_type}_price")
            second_flight.selected_class = class_type
            second_flight.selected_price = getattr(second_flight, f"{class_type}_price")
    
    return flights

#Ritorna un volo specifico con l'id corrispondente
def get_flight_by_id(flight_id):
    return Flight.query.get(flight_id)

#Ritorna tutti i voli di una specifica compagnia aerea
def get_flights_by_airline(airline_id): 
    return Flight.query.filter(Flight.airline_id == airline_id).all()

# Aggiunge un biletto al database
def book_ticket(flight_id, passenger_id, seat_number, ticket_class):
    #! prob da sostituire con un unique su seat_number
    if not Ticket.query.filter_by(flight_id=flight_id, seat_number=seat_number).first():
        selected_flight = Flight.query.get(flight_id)
        price = 0.0
        if ticket_class == 'economy':
            price = selected_flight.economy_price
        elif ticket_class == 'business':
            price = selected_flight.business_price
        elif ticket_class == 'first_class':
            price = selected_flight.first_class_price
        
        new_ticket = Ticket(
            flight_id=flight_id,
            passenger_id=passenger_id,
            seat_number=seat_number,
            ticket_class=ticket_class,
            price=price
            )
        db.session.add(new_ticket)
        db.session.commit()
        return True , None 
    else :
        return False , "Seat already booked."

def get_airplanes_by_airline(airline_id):
    return Airplane.query.filter_by(airline_id=airline_id).all()

def get_user_tickets(user_id):
    """
    ottiene tutti i biglietti di un utente
    """
    try:
        tickets = Ticket.query.filter_by(passenger_id = user_id).all()
        return tickets
    except Exception as e:
        print(f"Error getting user tickets {e}")
        return []


# def get_all_airports():
#     try:
#         airports = Airp