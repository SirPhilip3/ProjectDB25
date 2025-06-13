from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String , ForeignKey, Integer , Table, LargeBinary
from database import db
import uuid

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id : Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username : Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    password : Mapped[str] = mapped_column(nullable=False)

    def __repr__(self):
        return f"<User {self.username} Password {self.password}>"
    
class Airlines(UserMixin, db.Model):
    __tablename__ = 'airlines'

    id : Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name : Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    revenue : Mapped[str] = mapped_column(String(150), unique=True, nullable=False)

    def __repr__(self):
        return f"<Airline {self.name} Revenue {self.revenue}>"
    
class Passenger(UserMixin, db.Model):
    __tablename__ = 'passengers'

    id : Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username : Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    email : Mapped[str] = mapped_column(String(150), unique=True, nullable=False)

    def __repr__(self):
        return f"<User {self.username} Email {self.email}>"
    
