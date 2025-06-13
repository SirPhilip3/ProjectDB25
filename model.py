from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String , ForeignKey, Integer , Table, LargeBinary, Float
from database import db
import uuid

 # usiamo stesso UserMixin per tutti gli utenti, sia airline che passenger
 # diffenrenziamo per fare le query attraverso il campo boolean is_airline 

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id : Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username : Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    # per fare differenza tra airline e passenger usiamo campo boolean
    role : Mapped[bool] = mapped_column(default=None, nullable=False) 
    password : Mapped[str] = mapped_column(nullable=False)

    def __repr__(self):
        return f"<User {self.username} Type {self.role} Password {self.password}>"
    
class Airlines(UserMixin, db.Model):
    __tablename__ = 'airlines'

    id : Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name : Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    revenue : Mapped[str] = mapped_column(String(150), unique=False, nullable=True)

    def __repr__(self):
        return f"<Airline {self.name} Revenue {self.revenue}>"
    
class Passenger(UserMixin, db.Model):
    __tablename__ = 'passengers'

    id : Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username : Mapped[str] = mapped_column(String(150), unique=True, nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"
    
class Flight(db.Model):
    __tablename__ = 'flights'

    id : Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    departure : Mapped[str] = mapped_column(String(150), nullable=False)
    arrival : Mapped[str] = mapped_column(String(150), nullable=False)
    airline_id : Mapped[str] = mapped_column(String(36), ForeignKey('airlines.id'), nullable=False)
    airplane_id : Mapped[str] = mapped_column(String(36), ForeignKey('airplanes.id'), nullable=False)
    
    economy_price : Mapped[float] = mapped_column(Float, nullable=False)
    business_price : Mapped[float] = mapped_column(Float, nullable=False)
    first_class_price : Mapped[float] = mapped_column(Float, nullable=False)

    def __repr__(self):
        return f"<Departure {self.departure} Arrival {self.arrival}>"
    
class Airplane(db.Model):
    __tablename__ = 'airplanes'

    id : Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    model : Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    capacity : Mapped[int] = mapped_column(Integer, nullable=False)
    economy_seats : Mapped[int] = mapped_column(Integer, nullable=False)
    business_seats : Mapped[int] = mapped_column(Integer, nullable=False)
    first_class_seats : Mapped[int] = mapped_column(Integer, nullable=False)
    airline_id : Mapped[str] = mapped_column(String(36), ForeignKey('airlines.id'), nullable=False)

    def __repr__(self):
        return f"<Airplane {self.model} Capacity {self.capacity}>"

class Ticket(db.Model):
    __tablename__ = 'tickets'

    id : Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    flight_id : Mapped[str] = mapped_column(String(36), ForeignKey('flights.id'), nullable=False)
    passenger_id : Mapped[str] = mapped_column(String(36), ForeignKey('passengers.id'), nullable=False)
    seat_number : Mapped[str] = mapped_column(String(10), nullable=False)
    class_type : Mapped[str] = mapped_column(String(20), nullable=False) 

    def __repr__(self):
        return f"<Ticket Flight {self.flight_id} Passenger {self.passenger_id} Seat {self.seat_number}>"

