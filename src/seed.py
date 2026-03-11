from sqlmodel import Session, select
from src.models import User, Airport, Flight, Seat, FlightInstance
from src.database import engine
from datetime import datetime, timedelta


def run_seeder():
    """
    Create minimal flight infrastructure for testing.
    Idempotent: checks if data exists before creating.
    Assumes database tables already exist (they're created by init_db() or docker-compose).

    Returns: (instance_id, first_seat_id) for booking tests
    """
    with Session(engine) as session:
        # 1. Check/Create Airport
        airport = session.exec(
            select(Airport).where(Airport.code == "TEST")
        ).first()

        if not airport:
            airport = Airport(
                name="Test Airport",
                code="TEST",
                city="Test City",
                timezone="UTC"
            )
            session.add(airport)
            session.commit()

        # 2. Check/Create Flight
        flight = session.exec(
            select(Flight).where(Flight.flight_id == "TEST001")
        ).first()

        if not flight:
            flight = Flight(
                flight_id="TEST001",
                airline_code="TST",
                departure_airport_id=airport.id,
                arrival_airport_id=airport.id,
            )
            session.add(flight)
            session.commit()

        # 3. Check/Create FlightInstance
        instance = session.exec(
            select(FlightInstance).where(
                FlightInstance.flight_id == flight.id
            )
        ).first()

        if not instance:
            instance = FlightInstance(
                flight_id=flight.id,
                scheduled_departure=datetime(2026, 5, 20),
                base_price=450.00,
            )
            session.add(instance)
            session.commit()

        # 4. Check/Create Seats (exactly 100)
        seat_count = session.exec(
            select(Seat).where(Seat.instance_id == instance.id)
        ).all()

        if len(seat_count) == 0:
            seats = []
            for i in range(1, 101):
                seats.append(
                    Seat(
                        instance_id=instance.id,
                        seat_number=f"{i}A",
                        class_="economy",
                        status="available"
                    )
                )
            session.add_all(seats)
            session.commit()

        # Get the first seat ID for testing
        first_seat = session.exec(
            select(Seat).where(Seat.instance_id == instance.id).limit(1)
        ).first()
        
        return instance.id, first_seat.id if first_seat else 1


def populate_sample_data():
    """Extensive sample data population"""
    with Session(engine) as session:
        # 1. Add Multiple Airports
        airports = [
            Airport(
                name="John F. Kennedy", code="JFK", city="New York", timezone="EST"
            ),
            Airport(
                name="Los Angeles Intl", code="LAX", city="Los Angeles", timezone="PST"
            ),
            Airport(name="Heathrow", code="LHR",
                    city="London", timezone="GMT"),
            Airport(name="Haneda", code="HND", city="Tokyo", timezone="JST"),
        ]
        session.add_all(airports)
        session.commit()

        # 2. Define Flight Routes
        routes = [
            Flight(
                flight_id="AA100",
                airline_code="AA",
                departure_airport_id=airports[0].id,
                arrival_airport_id=airports[1].id,
            ),
            Flight(
                flight_id="BA200",
                airline_code="BA",
                departure_airport_id=airports[2].id,
                arrival_airport_id=airports[0].id,
            ),
            Flight(
                flight_id="JL300",
                airline_code="JL",
                departure_airport_id=airports[3].id,
                arrival_airport_id=airports[1].id,
            ),
        ]
        session.add_all(routes)
        session.commit()

        # 3. Create Multiple Instances for each Route
        # This gives you plenty of targets for your performance tests
        for route in routes:
            for day in range(1, 4):  # Next 3 days
                instance = FlightInstance(
                    flight_id=route.id,
                    scheduled_departure=datetime(
                        2026, 5, 20) + timedelta(days=day),
                    base_price=300.00 + (day * 50),
                )
                session.add(instance)
                session.commit()  # Commit to get instance.id for seats

                # 4. Generate Seats Automatically
                # Create 5 Business (1-5) and 15 Economy (6-20) seats per instance
                seats = []
                for i in range(1, 21):
                    seat_class = "business" if i <= 5 else "economy"
                    seats.append(
                        Seat(
                            instance_id=instance.id,
                            seat_number=f"{i}A",
                            class_=seat_class,
                        )
                    )
                session.add_all(seats)

        # 5. Add a few test Users
        users = [
            User(name="Alice Smith", email="alice@test.com",
                 password="hash123_secure"),
            User(name="Bob Jones", email="bob@test.com",
                 password="hash456_secure"),
            User(
                name="Charlie Brown",
                email="charlie@test.com",
                password="hash789_secure",
            ),
        ]
        session.add_all(users)

        session.commit()
        print(
            f"Success! Created {len(airports)} airports, {len(routes)} routes, and many seats."
        )
