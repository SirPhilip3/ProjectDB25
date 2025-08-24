import enum
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.orm import Mapped, mapped_column , relationship
from sqlalchemy import String , ForeignKey, Integer , Table, LargeBinary, Float, Enum, DateTime ,CheckConstraint ,Index, JSON, UniqueConstraint
from database import db
import uuid

# usiamo stesso UserMixin per tutti gli utenti, sia airline che passenger
# diffenrenziamo per fare le query attraverso il campo boolean role 

# Usiamo un Enum per i ruoli
class UserRole(enum.Enum):
    PASSENGER = 'passenger'
    AIRLINE = 'airline'

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    #! potrebbe essere ridondante userame e name se user è una compagnia aerea
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False) # La password dovrebbe essere più lunga per l'hash
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False)

    # Relazione: se l'utente è una compagnia, avrà un profilo airline associato
    airline_profile: Mapped["Airline"] = relationship(back_populates="user", cascade="all, delete-orphan")
    # Relazione: se l'utente è un passeggero, avrà delle prenotazioni
    # bookings: Mapped[list["Booking"]] = relationship(back_populates="passenger")

    def __repr__(self):
        return f"<User {self.email} (Role: {self.role.value})>"

class Airline(db.Model):
    __tablename__ = 'airlines'
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    
    # Chiave esterna per collegare la compagnia all'utente che la gestisce
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'), unique=True)
    
    # Relazioni
    user: Mapped["User"] = relationship(back_populates="airline_profile")
    flights: Mapped[list["Flight"]] = relationship(back_populates="airline")
    airplanes: Mapped[list["Airplane"]] = relationship(back_populates="airline")

    def __repr__(self):
        return f"<Airline {self.name}>"

class Airplane(db.Model):
    __tablename__ = 'airplanes'

    id : Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    model : Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    #! maybe useless
    capacity : Mapped[int] = mapped_column(Integer, nullable=False)
    # seat types
    economy_seats: Mapped[int] = mapped_column(Integer, nullable=False)
    business_seats: Mapped[int] = mapped_column(Integer, nullable=False)
    first_class_seats: Mapped[int] = mapped_column(Integer, nullable=False)

    # check total capacity < sum of all seats
    __table_args__ = (
        CheckConstraint(
            'capacity <= economy_seats + business_seats + first_class_seats', name='check_capacity_seats_sum'
        ),
    )
    
    airline_id: Mapped[str] = mapped_column(ForeignKey('airlines.id'), nullable=False)
    airline: Mapped["Airline"] = relationship(back_populates="airplanes")
    # Per eliminare "a cascata" i flight collegati a questo aereo
    flights: Mapped[list["Flight"]] = relationship(back_populates="airplane", cascade="all, delete-orphan", passive_deletes=True)

    def __repr__(self):
        return f"<Airplane {self.model} Capacity {self.capacity}>"

#! INUTILE
#? usata se volessimo modellare gli aereoporti
# class Airport(db.Model):
#     __tablename__ = 'airports'
    
#     id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
#     #? name maybe unique
#     name: Mapped[str] = mapped_column(String(150), nullable=False)
#     city: Mapped[str] = mapped_column(String(150), nullable=False)
#     iata_code: Mapped[str] = mapped_column(String(3), unique=True, nullable=False) # es. "FCO" per Fiumicino

#     def __repr__(self):
#         return f"<Airport {self.name} , {self.city} ({self.iata_code})>"

class Flight(db.Model):
    __tablename__ = 'flights'
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    departure_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    arrival_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False)

    departure_airport: Mapped[str] = mapped_column(String(100), nullable=False)
    destination_airport: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Prezzi base per classe
    economy_price: Mapped[float] = mapped_column(Float, nullable=False)
    business_price: Mapped[float] = mapped_column(Float, nullable=False)
    first_class_price: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Chiavi esterne
    airline_id: Mapped[str] = mapped_column(ForeignKey('airlines.id'), nullable=False)
    airplane_id: Mapped[str] = mapped_column(ForeignKey('airplanes.id', ondelete='CASCADE'),nullable=False)

    # Relazioni
    airline: Mapped["Airline"] = relationship(back_populates="flights") 
    tickets: Mapped[list["Ticket"]] = relationship(back_populates="flight",cascade="all, delete-orphan", passive_deletes=True)
    airplane: Mapped["Airplane"] = relationship(back_populates="flights")

    extras: Mapped[dict] = mapped_column(JSON, nullable=True) # Lista di extra disponibili [{"name":name, "price": price}, ...]

    #! non usato (se volessimo per usare la tabella airport)
    # departure_airport: Mapped["Airport"] = relationship(foreign_keys=[departure_airport_id])
    # destination_airport: Mapped["Airport"] = relationship(foreign_keys=[destination_airport_id])
    # departure_airport_id: Mapped[int] = mapped_column(ForeignKey('airports.id'), nullable=False)
    # destination_airport_id: Mapped[int] = mapped_column(ForeignKey('airports.id'), nullable=False)

    # Constraints
    __table_args__ = (
        CheckConstraint('departure_airport != destination_airport', name='check_different_airports'),
        CheckConstraint('arrival_time > departure_time', name='check_arrival_after_departure'),
        CheckConstraint('economy_price >= 0', name='check_non_negative_economy_price'),
        CheckConstraint('business_price >= 0', name='check_non_negative_business_price'),
        CheckConstraint('first_class_price >= 0', name='check_non_negative_first_class_price'),
        # Index('idx_flight_route_time', 'departure_airport_id', 'destination_airport_id', 'departure_time'),
        Index('idx_flight_airline_time', 'airline_id', 'departure_time'),
    )


    @property
    def duration(self):
        """Calcola la durata del volo in minuti"""
        if self.departure_time and self.arrival_time:
            delta = self.arrival_time - self.departure_time
            return int(delta.total_seconds() / 60 )
        return 0
    

    @property
    def available_seats(self):
        """Calcola i posti disponibili per classe"""
        if not self.airplane:
            return {'economy': 0, 'business': 0, 'first_class': 0}
        
        # Conta i biglietti venduti per classe
        sold_economy = len([t for t in self.tickets if t.ticket_class == 'economy'])
        sold_business = len([t for t in self.tickets if t.ticket_class == 'business'])
        sold_first = len([t for t in self.tickets if t.ticket_class == 'first_class'])
        
        return {
            'economy': max(0, self.airplane.economy_seats - sold_economy),
            'business': max(0, self.airplane.business_seats - sold_business),
            'first_class': max(0, self.airplane.first_class_seats - sold_first)
        }



    def __repr__(self):
        return f"<Flight {self.id} from {self.departure_airport} to {self.destination_airport}>"


#! INUTILE
# class Booking(db.Model):
#     __tablename__ = 'bookings'

#     id: Mapped[int] = mapped_column(primary_key=True)
#     booking_date: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=db.func.now())
#     total_cost: Mapped[float] = mapped_column(Float, nullable=False)
    
#     # Chiave esterna per il passeggero che ha fatto la prenotazione

    
#     # Relazioni
#     passenger: Mapped["User"] = relationship(back_populates="bookings")
#     tickets: Mapped[list["Ticket"]] = relationship(back_populates="booking", cascade="all, delete-orphan")

class Ticket(db.Model):
    __tablename__ = 'tickets'
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    seat_number: Mapped[str] = mapped_column(String(10), nullable=False)  # Numero di posto unico
    ticket_class: Mapped[str] = mapped_column(String(20), nullable=False) # 'economy', 'business', 'first'
    price: Mapped[float] = mapped_column(Float, nullable=False)
    selected_extras: Mapped[dict] = mapped_column(JSON, nullable=True)  # Lista di dizionari per gli extra selezionati
    
    passenger_id: Mapped[str] = mapped_column(ForeignKey('users.id'), nullable=False)
    # Chiavi esterne
    flight_id: Mapped[int] = mapped_column(ForeignKey('flights.id', ondelete='CASCADE'), nullable=False)
    
    # Relazioni
    flight: Mapped["Flight"] = relationship(back_populates="tickets")
    
    #!
    __table_args__ = (
        UniqueConstraint('seat_number', 'flight_id', name='unique_seat_per_flight'),
    )

    def __repr__(self):
        return f"<Ticket {self.id} for flight {self.flight_id} - {self.ticket_class} class , Passenger {self.passenger_id}>"