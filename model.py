import enum
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.orm import Mapped, mapped_column , relationship
from sqlalchemy import String , ForeignKey, Integer , Table, LargeBinary, Float, Enum, DateTime ,CheckConstraint ,Index, JSON, UniqueConstraint
from database import db
import uuid

# Usiamo un Enum per i ruoli
class UserRole(enum.Enum):
    PASSENGER = 'passenger'
    AIRLINE = 'airline'

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False)
    
    # Campi opzionali
    phone: Mapped[str] = mapped_column(String(255), nullable=True)
    address: Mapped[str] = mapped_column(String(255), nullable=True)
    firstname: Mapped[str] = mapped_column(String(255), nullable=True)
    lastname: Mapped[str] = mapped_column(String(255), nullable=True)
    
    # Relazione: se l'utente è una compagnia, avrà un profilo airline associato
    airline_profile: Mapped["Airline"] = relationship(back_populates="user", cascade="all, delete-orphan")

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
    capacity : Mapped[int] = mapped_column(Integer, nullable=False)
    # seat types
    economy_seats: Mapped[int] = mapped_column(Integer, nullable=False)
    business_seats: Mapped[int] = mapped_column(Integer, nullable=False)
    first_class_seats: Mapped[int] = mapped_column(Integer, nullable=False)

    # Controlla che capacity <= somma di tutti i posti
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

    # Constraints
    __table_args__ = (
        CheckConstraint('departure_airport != destination_airport', name='check_different_airports'),
        CheckConstraint('arrival_time > departure_time', name='check_arrival_after_departure'),
        CheckConstraint('economy_price >= 0', name='check_non_negative_economy_price'),
        CheckConstraint('business_price >= 0', name='check_non_negative_business_price'),
        CheckConstraint('first_class_price >= 0', name='check_non_negative_first_class_price'),
        Index('idx_flight_airline_time', 'airline_id', 'departure_time'),
    )

    def __repr__(self):
        return f"<Flight {self.id} from {self.departure_airport} to {self.destination_airport}>"

class Ticket(db.Model):
    __tablename__ = 'tickets'
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    seat_number: Mapped[str] = mapped_column(String(10), nullable=False)  # Numero di posto unico
    ticket_class: Mapped[str] = mapped_column(String(20), nullable=False) # 'economy', 'business', 'first'
    price: Mapped[float] = mapped_column(Float, nullable=False)
    selected_extras: Mapped[dict] = mapped_column(JSON, nullable=True)  # Lista di dizionari per gli extra selezionati
    
    passenger_id: Mapped[str] = mapped_column(ForeignKey('users.id'), nullable=False)

    flight_id: Mapped[int] = mapped_column(ForeignKey('flights.id', ondelete='CASCADE'), nullable=False)
    
    flight: Mapped["Flight"] = relationship(back_populates="tickets")
    
    __table_args__ = (
        UniqueConstraint('seat_number', 'flight_id', name='unique_seat_per_flight'),
    )

    def __repr__(self):
        return f"<Ticket {self.id} for flight {self.flight_id} - {self.ticket_class} class , Passenger {self.passenger_id}>"