# crud operations for the database

from database import db
from model import User , Flight, Airplane, Airlines, Passenger
from sqlalchemy.orm import aliased

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


def add_airplane() :

#! deve ritornare un oggetto con :
# departure_time , arrival_time, price ( price depends on class_type ) 
def search_flight(departure, arrival, direct_flight, class_type):
    if direct_flight:
        result = db.session.query(Flight.departure_airport, Flight.destination_airport).filter(
            Flight.departure_airport == departure, Flight.destination_airport == arrival).all()
    else:
        F1 = aliased(Flight)
        F2 = aliased(Flight)
        rows = db.session.query(F1.departure_airport, F1.destination_airport).filter(
            F1.departure_airport == departure,
            F1.destination_airport == F2.departure_airport,
            F2.destination_airport == arrival
            ).all()
        
    result = []
    for dep, dest in rows:
        result.append((dep, dest, class_type))
    match class_type:
        case "Economy":
            result.departure_airport
        case "Business":
            a=1
        case "First Class":
            a=1

    return result


def get_flight_by_id(flight_id):
    return Flight.query.get(flight_id)

def get_flights_by_airline(airline_id): 

# deve aggiunere un biletto al database
def book_ticket(flight_id, passenger_id, seat_number, class_type):    
    
    