# crud operations for the database
from database import db
from model import User , Flight, Airplane, Airlines, Passenger, Ticket
from sqlalchemy.orm import aliased

# Aggiunge una tratta al database
def add_flight(airline_id, airplane_id, departure, arrival, economy_price, business_price, first_class_price):
    new_flight = Flight(
        airline_id=airline_id,
        airplane_id=airplane_id,
        departure=departure,
        arrival=arrival,
        economy_price=economy_price,
        business_price=business_price,
        first_class_price=first_class_price
    )
    db.session.add(new_flight)
    db.session.commit()

# Aggiunge un aereoplano al database
def add_airplane(model, capacity, economy_seats,business_seats,first_class_seats, airline_id):
    if capacity < (economy_seats + business_seats + first_class_seats):
        raise ValueError("Capacity must be >= sum of all seats.")
    
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

# Ritorna i voli diretti o indiretti filtrati con i parametri corrispondenti
def search_flight(departure, arrival, direct_flight, class_type):
    if direct_flight:
        rows = db.session.query(Flight.departure_airport, 
                                Flight.destination_airport, 
                                Flight.economy_price, 
                                Flight.business_price, 
                                Flight.first_class_price).filter(
                                    Flight.departure_airport == departure, 
                                    Flight.destination_airport == arrival).all()
    else:
        F1 = aliased(Flight)
        F2 = aliased(Flight)
        rows = db.session.query(F1.departure_airport, 
                                F1.destination_airport, 
                                F1.economy_price, 
                                F1.business_price, 
                                F1.first_class_price).filter(
                                    F1.departure_airport == departure,
                                    F1.destination_airport == F2.departure_airport,
                                    F2.destination_airport == arrival).all()
    result = []
    match class_type:
        case "Economy":
            for dep, dest, e_price, b_price, f_price in rows:
                result.append((dep, dest, e_price))
        case "Business":
            for dep, dest, e_price, b_price, f_price in rows:
                result.append((dep, dest, b_price))
        case "First Class":
            for dep, dest, e_price, b_price, f_price in rows:
                result.append((dep, dest, f_price))
    return result

#Ritorna un volo specifico con l'id corrispondente
def get_flight_by_id(flight_id):
    return Flight.query.get(flight_id)

#Ritorna tutti i voli di una specifica compagnia aerea
def get_flights_by_airline(airline_id): 
    return Flight.query.filter_by(Flight.airline_id == airline_id).all()

# Aggiunge un biletto al database
def book_ticket(flight_id, passenger_id, seat_number, class_type):    
    if not Ticket.query.filter_by(flight_id=flight_id, seat_number=seat_number).first():
        new_ticket = Ticket(
            flight_id=flight_id,
            passenger_id=passenger_id,
            seat_number=seat_number,
            ticket_class=class_type
            )
        db.session.add(new_ticket)
        db.session.commit()