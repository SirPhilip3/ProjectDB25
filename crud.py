# crud operations for the database
from database import db
from model import User , Flight, Airplane, Airline, Ticket
from sqlalchemy.orm import aliased 
from sqlalchemy import text,func,desc
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

# Aggiunge una tratta al database , ritorna il nuovo volo
def add_flight(airline_id, airplane_id, departure_airport, arrival_airport ,departure_time, arrival_time, economy_price, business_price, first_class_price, extras=None):
    new_flight = Flight(
        airline_id=airline_id,
        airplane_id=airplane_id,
        departure_airport=departure_airport,
        destination_airport=arrival_airport,
        departure_time=departure_time,
        arrival_time=arrival_time,
        economy_price=economy_price,
        business_price=business_price,
        first_class_price=first_class_price,
        extras=extras
    )
    try:
        db.session.add(new_flight)
        db.session.commit()
        return new_flight
    except Exception as e:
        print(f"Error adding flight {e}")
        db.session.rollback()
        return redirect(url_for('add_flight_page'))

# Aggiunge un aereoplano al database, ritorna il nuovo aereo
def add_airplane(model, capacity, economy_seats, business_seats, first_class_seats, airline_id):
    new_airplane = Airplane(
        model=model,
        capacity=capacity,
        economy_seats=economy_seats,
        business_seats=business_seats,
        first_class_seats=first_class_seats,
        airline_id=airline_id
    )
    try:
        db.session.add(new_airplane)
        db.session.commit()
        return new_airplane
    except Exception as e:
        print(f"Error adding airplane {e}")
        db.session.rollback()
        return redirect(url_for('add_airplane_page'))

def delete_flight_by_id(flight_id):
    flight = Flight.query.get(flight_id)
    if flight:
        db.session.delete(flight)
        db.session.commit()

def delete_airplane_by_id(airplane_id):
    airplane = Airplane.query.get(airplane_id)
    if airplane:
        db.session.delete(airplane)
        db.session.commit()

def delete_ticket_by_id(ticket_id):
    ticket = Ticket.query.get(ticket_id)
    if ticket:
        db.session.delete(ticket)
        db.session.commit()

# Ritorna i voli diretti e/o indiretti filtrati con i parametri corrispondenti
#! da rivedere l'implemetazione
def search_flight(departure, arrival, direct_flight, class_type, min_price=None, max_price=None, sort_by=None):
#     if direct_flight:
#         query = Flight.query.filter(
#             Flight.departure_airport == departure, 
#             Flight.destination_airport == arrival)
#     else:
#         F1 = aliased(Flight)
#         F2 = aliased(Flight)
#         query = db.session.query(F1, F2).filter(
#             F1.departure_airport == departure,
#             F1.destination_airport == F2.departure_airport,
#             F2.destination_airport == arrival,
#             # devono essere separati da almeno 2 ore , potremmo aggiungere un limite massimo
#             F2.departure_time >= F1.arrival_time + timedelta(hours=2))
    
#     # Filtri per prezzo
#     #! implementazione diversa per i voli con uno stop 
#     if min_price:
#         min_price = float(min_price)
#         price_field = getattr(Flight, f"{class_type}_price")
#         query = query.filter(price_field >= min_price)
    
#     if max_price:
#         max_price = float(max_price)
#         price_field = getattr(Flight, f"{class_type}_price")
#         query = query.filter(price_field <= max_price)
    
#     # Ordinamento
#     if sort_by:
#         if sort_by == 'price_asc':
#             price_field = getattr(Flight, f"{class_type}_price")
#             query = query.order_by(price_field.asc())
#         elif sort_by == 'price_desc':
#             price_field = getattr(Flight, f"{class_type}_price")
#             query = query.order_by(price_field.desc())
#         elif sort_by == 'departure_asc':
#             query = query.order_by(Flight.departure_time.asc())
#         elif sort_by == 'departure_desc':
#             query = query.order_by(Flight.departure_time.desc())
#         elif sort_by == 'duration_asc':
#             query = query.order_by((Flight.arrival_time - Flight.departure_time).asc())
    
#     # Esegui la query
#     flights = query.all()
    
#     #! implementazione diversa per i voli con uno stop 
#     if direct_flight:
#         # aggiunge 2 campi temporanei per il tipo di classe e il prezzo selezionato
#         for flight in flights:
#             flight.selected_class = class_type
#             flight.selected_price = getattr(flight, f"{class_type}_price")
#     else:
#         # aggiunge 2 campi temporanei per il tipo di classe e il prezzo selezionato
#         for first_flight, second_flight in flights:
#             first_flight.selected_class = class_type
#             first_flight.selected_price = getattr(first_flight, f"{class_type}_price")
#             second_flight.selected_class = class_type
#             second_flight.selected_price = getattr(second_flight, f"{class_type}_price")
    
#     return flights

    flights = Flight.query.filter(
        Flight.departure_airport== departure, 
        Flight.destination_airport == arrival).all()
    # Converto i voli diretti in coppiedi voli dove il secondo è None
    flights = [(flight, None) for flight in flights]

    if not direct_flight:
        F1 = aliased(Flight)
        F2 = aliased(Flight)
        flights_aux = db.session.query(F1, F2).filter(
            F1.departure_airport == departure,
            F1.destination_airport == F2.departure_airport,
            F2.destination_airport == arrival,
            # devono essere separati da almeno 2 ore , potremmo aggiungere un limite massimo
            F2.departure_time >= F1.arrival_time + timedelta(hours=2)).all()
        # Aggiungo in coda ai voli diretti i voli con scalo
        flights.extend(flights_aux)
    
    # Filtri per prezzo
    if min_price:
        min_price = float(min_price)
        price_field = getattr(Flight, f"{class_type}_price")
        flights = [(f1, f2) for f1, f2 in flights if (
            (f2 is None and f1.selected_price >= min_price) or 
            (f2 is not None and (f1.selected_price + f2.selected_price) >= min_price))]
    if max_price:
        max_price = float(max_price)
        price_field = getattr(Flight, f"{class_type}_price")
        flights = [(f1, f2) for f1, f2 in flights if (
        (f2 is None and f1.selected_price <= max_price) or 
        (f2 is not None and (f1.selected_price + f2.selected_price) <= max_price))]
    
    # Ordinamento
    if sort_by:
        if sort_by == 'price_asc':
            price_field = getattr(Flight, f"{class_type}_price")
            flights.sort(key=lambda pair: (
            pair[0].selected_price if pair[1] is None 
            else pair[0].selected_price + pair[1].selected_price))
        elif sort_by == 'price_desc':
            price_field = getattr(Flight, f"{class_type}_price")
            flights.sort(key=lambda pair: (
            pair[0].selected_price if pair[1] is None 
            else pair[0].selected_price + pair[1].selected_price), reverse=True)
        elif sort_by == 'departure_asc':
            flights.sort(key=lambda pair: pair[0].departure_time)
        elif sort_by == 'departure_desc':
            flights.sort(key=lambda pair: pair[0].departure_time,reverse=True)
        elif sort_by == 'duration_asc':
            flights.sort(key=lambda pair: ((pair[0].arrival_time - pair[0].departure_time).total_seconds()
            if pair[1] is None else (pair[1].arrival_time - pair[0].departure_time).total_seconds()))

    # aggiunge 2 campi temporanei per il tipo di classe e il prezzo selezionato
    for first_flight, second_flight in flights:
        first_flight.selected_class = class_type
        first_flight.selected_price = getattr(first_flight, f"{class_type}_price")
        if second_flight:
            second_flight.selected_class = class_type
            second_flight.selected_price = getattr(second_flight, f"{class_type}_price")
    print(flights)
    return flights

#Ritorna un volo specifico con l'id corrispondente
def get_flight_by_id(flight_id):
    return Flight.query.get(flight_id)

#Ritorna tutti i voli di una specifica compagnia aerea
def get_flights_by_airline(airline_id): 
    return Flight.query.filter(Flight.airline_id == airline_id).all()

# Aggiunge un biletto al database
def book_ticket(flight_id, passenger_id, seat_number, ticket_class, selected_extras=None):

    try:
        selected_flight = Flight.query.get(flight_id)
        price = 0.0
        if ticket_class == 'economy':
            price = selected_flight.economy_price
        elif ticket_class == 'business':
            price = selected_flight.business_price
        elif ticket_class == 'first_class':
            price = selected_flight.first_class_price
            
        #! price potrebbe essere inutile se abbiamo la classe + gli extra potremmo calcolarla dopo
        if selected_extras :
            for extra in selected_extras :
                price += extra['price']
        
        new_ticket = Ticket(
            flight_id=flight_id,
            passenger_id=passenger_id,
            seat_number=seat_number,
            ticket_class=ticket_class,
            price=price,
            selected_extras=selected_extras
            )
        db.session.add(new_ticket)
        db.session.commit()
        return True , None 
    except Exception as e:
        db.session.rollback()
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

def get_airline_by_id(airline_id):
    """
    Ritorna una compagnia aerea specifica con l'id corrispondente
    """
    try:
        airline = Airline.query.get(airline_id)
        return airline
    except Exception as e:
        print(f"Error getting airline by id {e}")

def get_airline_statistics(airline_id):
    """
    Ritorna le statistiche generali di una compagnia aerea
    + numero di voli 
    + numero di aerei
    + numero di biglietti venduti 
    + ricavi totali
    """
    flights = get_flights_by_airline(airline_id)
    n_flights = len(flights)
    
    airplanes = get_airplanes_by_airline(airline_id)
    n_airplanes = len(airplanes)
    
    tickets = Ticket.query.join(Ticket.flight).filter(Flight.airline_id == airline_id).all()
    n_tickets = len(tickets)

    total_revenue = sum(ticket.price for ticket in tickets)

    return n_flights, n_airplanes, n_tickets, total_revenue

#! #! da testare
def get_airline_top_routes(airline_id, limit=10):
    """
    Ottiene le tratte più richieste di una compagnia aerea
    """
    try:
        # Query per ottenere le rotte con più passeggeri
        route_stats = db.session.query(
            Flight.departure_airport,
            Flight.destination_airport,
            func.count(Ticket.id).label('passengers'),
       
        ).join(
            Ticket, Flight.id == Ticket.flight_id
        ).filter(
            Flight.airline_id == airline_id,  
        ).group_by(
            Flight.departure_airport,
            Flight.destination_airport
        ).order_by(
            desc('passengers')
        ).limit(limit).all()
        
        top_routes = []
        for route in route_stats:
            top_routes.append({
                'route': f"{route.departure_airport} → {route.destination_airport}",
                'passengers': route.passengers,
               
            })
        
        return top_routes
        
    except Exception as e:
        print(f"Error getting top routes: {e}")
        return []



#! da testare
def get_airline_class_distribution(airline_id):
    """
    Ottiene la distribuzione dei passeggeri per classe
    """
    try:
        class_stats = db.session.query(
            Ticket.ticket_class,
            func.count(Ticket.id).label('count'),

            
        ).join(
            Flight, Ticket.flight_id == Flight.id
        ).filter(
            Flight.airline_id == airline_id,
        ).group_by(
            Ticket.ticket_class
        ).all()
        
        distribution = {}
        for stat in class_stats:
            distribution[stat.ticket_class] = {
                'passengers': stat.count,
            }
        
        return distribution
        
    except Exception as e:
        print(f"Error getting class distribution: {e}")
        return {}


def get_remaining_ticket_count_by_flight(flight_id):
    """
    Ottiene il numero rimanente di biglietti venduti per un volo specifico
    """

    try:
        flight_id = str(flight_id)
        airplane = Flight.query.get(flight_id).airplane
        tickets = Ticket.query.join(Ticket.flight).filter(Flight.id == flight_id).all()
        n_economy , n_business, n_first_class = 0, 0, 0
        for ticket in tickets:
            if ticket.ticket_class == 'economy':
                n_economy += 1
            elif ticket.ticket_class == 'business':
                n_business += 1
            elif ticket.ticket_class == 'first_class':
                n_first_class += 1
        return {
            'economy': airplane.economy_seats-n_economy,
            'business': airplane.business_seats-n_business,
            'first_class': airplane.first_class_seats - n_first_class,
            'total': airplane.capacity - len(tickets)
        }
    except Exception as e:
        print(f"Error getting ticket count by flight {e}")

#! non usato 
# def search_airport(name, city, iata_code):
#     """
#     Cerca un aeroporto in base al nome, città o codice IATA
#     """
#     try:
#         query = Airport.query.filter_by(
#             name = name,
#             city = city,
#             iata_code = iata_code
#         ).first()
#         return query
#     except Exception as e:
#         print(f"Error searching airport {e}")

# def search_airport_by_iata(iata_code):
#     """
#     Cerca un aeroporto in base al codice IATA
#     """
#     try:
#         query = Airport.query.filter_by(iata_code=iata_code).first()
#         return query
#     except Exception as e:
#         print(f"Error searching airport by IATA {e}")

# def get_airport_by_id(airport_id):
#     """
#     Ritorna un aeroporto specifico con l'id corrispondente
#     """
#     try:
#         airports = Airport.query.filter_by(id=airport_id).all()
#         return airports
#     except Exception as e:
#         print(f"Error getting airport by id {e}")
#         return None

# # Aggiunge un aeroporto al database, ritorna il nuovo aeroporto
# def add_airport(name, city, iata_code):
#     """
#     Aggiunge un aeroporto al database, ritorna il nuovo aeroporto
#     """
#     new_airport = Airport(
#         name=name,
#         city=city,
#         iata_code=iata_code
#     )
#     try :
#         db.session.add(new_airport)
#         db.session.commit()
#         return new_airport
#     except Exception as e:
#         db.session.rollback()  
#         print(f"Error adding airport {e}")
#         return None

# def get_all_airports():
#     """
#     ottiene tutti gli aeroporti
#     """
#     try:
#         airports = Airport.query.all()
#         return airports
#     except Exception as e:
#          print(f"Error getting airports {e}")
#          return[]