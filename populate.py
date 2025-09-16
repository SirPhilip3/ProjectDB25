# from app import app
from database import db, app
from model import UserRole, User , Flight, Airplane, Airline, Ticket
from datetime import datetime
from werkzeug.security import generate_password_hash

def populate_db_with_demo_data():
    with app.app_context():
        # Cancella dati precedenti
        db.drop_all()
        db.create_all()
        
        # ====== CREAZIONE UTENTI ======
        passenger1 = User(
            email="mario.rossi@gmail.com",
            password=generate_password_hash("password123", method='pbkdf2:sha256'),
            role=UserRole.PASSENGER,
            firstname="Mario",
            lastname="Rossi",
            phone="+39 3456789012",
            address="Via Roma 10, Milano"
        )
        passenger2 = User(
            email="luigi.verdi@gmail.com",
            password=generate_password_hash("pass123word", method='pbkdf2:sha256'),
            role=UserRole.PASSENGER,
            firstname="Luigi",
            lastname="Verdi",
            phone="+39 5578783147",
            address="Via Verdi 2, Milano"
        )
        passenger3 = User(
            email="lucia.Bianchi@gmail.com",
            password=generate_password_hash("123password", method='pbkdf2:sha256'),
            role=UserRole.PASSENGER,
            firstname="Lucia",
            lastname="Bianchi",
            phone="+39 4867103486",
            address="Via Garibaldi 3, Palermo"
        )

        db.session.add_all([passenger1, passenger2, passenger3])
        db.session.commit()   

        airline_user1 = User(
            email="airitaly@gmail.com",
            password=generate_password_hash("securepass", method='pbkdf2:sha256'),
            role=UserRole.AIRLINE,
            phone="+39 0022765657",
            address="Viale Europa 22, Roma"
        )
        airline_user2 = User(
            email="flysafe@gmail.com",
            password=generate_password_hash("pass0044", method='pbkdf2:sha256'),
            role=UserRole.AIRLINE,
            phone="+39 34658633",
            address="Via Cavour 33, Treviso"
        )

        db.session.add_all([airline_user1, airline_user2])
        db.session.commit()

        # ====== CREAZIONE COMPAGNIE AEREE ======
        airline1 = Airline(
            name="Air Italy",
            user=airline_user1
        )
        airline2 = Airline(
            name="Fly Safe",
            user=airline_user2
        )

        db.session.add_all([airline1, airline2])
        db.session.commit()
        # ====== CREAZIONE AEREI COLLEGATI ALLE COMPAGNIE ======
        # Compagnia 1
        airplane1 = Airplane(
            model="Boeing 737",
            capacity=180,
            economy_seats=150,
            business_seats=24,
            first_class_seats=6,
            airline=airline1
        )
        airplane2 = Airplane(
                model="Boeing 737 MAX",
                capacity=210,
                economy_seats=180,
                business_seats=24,
                first_class_seats=6,
                airline=airline1
            )
        # Compagnia 2
        airplane3 = Airplane(
            model="ATR 72",
            capacity=80,
            economy_seats=60,
            business_seats=10,
            first_class_seats=10,
            airline=airline2
        )

        db.session.add_all([airplane1, airplane2, airplane3])
        db.session.commit()

        # ====== CREAZIONE VOLI ======
        # Compagnia 1 Aereo 1
        flight1 = Flight(
                    departure_time=datetime(2025, 10, 1, 10, 30),
                    arrival_time=datetime(2025, 10, 1, 14, 10),
                    departure_airport="Roma",
                    destination_airport="Parigi",
                    economy_price=80.0,
                    business_price=250.0,
                    first_class_price=300.0,
                    airline=airline1,
                    airplane=airplane1,
                    extras=[
                        {"name": "Bagaglio aggiuntivo", "price": 30.0},
                        {"name": "Imbarco prioritario", "price": 15.0}
                    ]
                )
        # Compagnia 1 Aereo 2
        flight2 = Flight(
                    departure_time=datetime(2025, 11, 10, 9, 30),
                    arrival_time=datetime(2025, 11, 10, 10, 50),
                    departure_airport="Milano",
                    destination_airport="Londra",
                    economy_price=45.0,
                    business_price=70.0,
                    first_class_price=100.0,
                    airline=airline1,
                    airplane=airplane2,
                    extras=[
                        {"name": "Bagaglio aggiuntivo", "price": 30.0},
                        {"name": "Imbarco prioritario", "price": 15.0}
                    ]
                )
        # Compagnia 2 Aereo 1
        flight3 = Flight(
                    departure_time=datetime(2025, 10, 15, 18, 0),
                    arrival_time=datetime(2025, 10, 16, 3, 40),
                    departure_airport="Parigi",
                    destination_airport="Tokyo",
                    economy_price=180.0,
                    business_price=300.0,
                    first_class_price=400.0,
                    airline=airline2,
                    airplane=airplane3,
                    extras=[
                        {"name": "Bagaglio aggiuntivo", "price": 30.0},
                        {"name": "Imbarco prioritario", "price": 15.0},
                        {"name": "Beauty Case", "price": 20.0}
                    ]
                )
        
        flight4 = Flight(
            departure_time=datetime(2025, 10, 1, 10, 30),
            arrival_time=datetime(2025, 10, 1, 14, 10),
            departure_airport="Roma",
            destination_airport="Parigi",
            economy_price=85.0,
            business_price=260.0,
            first_class_price=320.0,
            airline=airline2,
            airplane=airplane3,
            extras=[
                {"name": "Bagaglio aggiuntivo", "price": 28.0},
                {"name": "Imbarco prioritario", "price": 12.0}
            ]
        )

        # Milano-Londra per Fly Safe (compagnia 2, aereo 3)
        flight5 = Flight(
            departure_time=datetime(2025, 11, 10, 9, 30),
            arrival_time=datetime(2025, 11, 10, 10, 50),
            departure_airport="Milano",
            destination_airport="Londra",
            economy_price=50.0,
            business_price=75.0,
            first_class_price=110.0,
            airline=airline2,
            airplane=airplane3,
            extras=[
                {"name": "Bagaglio aggiuntivo", "price": 32.0},
                {"name": "Imbarco prioritario", "price": 14.0}
            ]
        )

        # Parigi-Tokyo per Air Italy (compagnia 1, aereo 2)
        flight6 = Flight(
            departure_time=datetime(2025, 10, 15, 18, 0),
            arrival_time=datetime(2025, 10, 16, 3, 40),
            departure_airport="Parigi",
            destination_airport="Tokyo",
            economy_price=185.0,
            business_price=310.0,
            first_class_price=410.0,
            airline=airline1,
            airplane=airplane2,
            extras=[
                {"name": "Bagaglio aggiuntivo", "price": 30.0},
                {"name": "Imbarco prioritario", "price": 15.0},
                {"name": "Beauty Case", "price": 22.0}
            ]
        )

        flight7 = Flight(
            departure_time=datetime(2025, 12, 20, 15, 0),
            arrival_time=datetime(2025, 12, 20, 17, 30),
            departure_airport="Roma",
            destination_airport="Tokyo",
            economy_price=150.0,
            business_price=400.0,
            first_class_price=600.0,
            airline=airline1,
            airplane=airplane1,
            extras=[
                {"name": "Bagaglio aggiuntivo", "price": 40.0},
                {"name": "Imbarco prioritario", "price": 20.0},
                {"name": "Pasti speciali", "price": 25.0}
            ]
        )

        db.session.add_all([flight1, flight2, flight3, flight4, flight5, flight6, flight7])
        db.session.commit()
        # ====== CREAZIONE TICKETS ======
        # Passenger 1 Flight 1
        ticket1 = Ticket(
            seat_number="E3",
            ticket_class="economy",
            price=110.0,
            selected_extras=[{"name": "Bagaglio extra", "price": 30.0}],
            passenger_id=passenger1.id,
            flight_id=flight1.id
        )
        ticket2 = Ticket(
            seat_number="E4",
            ticket_class="economy",
            price=110.0,
            selected_extras=[{"name": "Bagaglio extra", "price": 30.0}],
            passenger_id=passenger1.id,
            flight_id=flight1.id
        )
        ticket3 = Ticket(
            seat_number="E10",
            ticket_class="economy",
            price=110.0,
            selected_extras=[{"name": "Bagaglio extra", "price": 30.0}],
            passenger_id=passenger1.id,
            flight_id=flight1.id
        )

        # Passenger 2 Flight 2
        ticket4 = Ticket(
            seat_number="F2",
            ticket_class="first_class",
            price=115.0,
            selected_extras=[{"name": "Imbarco prioritario", "price": 15.0}],
            passenger_id=passenger2.id,
            flight_id=flight2.id
        )
        ticket5 = Ticket(
            seat_number="F3",
            ticket_class="first_class",
            price=115.0,
            selected_extras=[{"name": "Imbarco prioritario", "price": 15.0}],
            passenger_id=passenger2.id,
            flight_id=flight2.id
        )
        ticket6 = Ticket(
            seat_number="F4",
            ticket_class="first_class",
            price=115.0,
            selected_extras=[{"name": "Imbarco prioritario", "price": 15.0}],
            passenger_id=passenger2.id,
            flight_id=flight2.id
        )

        # Passenger 3 Flight 3
        ticket7 = Ticket(
            seat_number="F7",
            ticket_class="first_class",
            price=420.0,
            selected_extras=[{"name": "Beauty Case", "price": 20.0}],
            passenger_id=passenger3.id,
            flight_id=flight3.id
        )
        ticket8 = Ticket(
            seat_number="E7",
            ticket_class="economy",
            price=200.0,
            selected_extras=[{"name": "Beauty Case", "price": 20.0}],
            passenger_id=passenger3.id,
            flight_id=flight3.id
        )
        ticket9 = Ticket(
                seat_number="B7",
                ticket_class="business",
                price=345.0,
                selected_extras=[
                        {"name": "Bagaglio aggiuntivo", "price": 30.0},
                        {"name": "Imbarco prioritario", "price": 15.0}],
                passenger_id=passenger3.id,
                flight_id=flight3.id
            )
    
        db.session.add_all([ticket1, ticket2, ticket3, ticket4, ticket5, ticket6, ticket7, ticket8, ticket9])
        db.session.commit()
        print("Database popolato correttamente")