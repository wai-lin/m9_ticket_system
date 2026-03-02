from sqlmodel import Session
from models.main import User, Airport, Flight, Seat, FlightInstance
from src.database import engine
from datetime import datetime, timedelta


def populate_sample_data():
    """Requirement 3: Extensive sample data population"""
    with Session(engine) as session:
        # 1. Add Multiple Airports
        airports = [
            Airport(
                name="John F. Kennedy", code="JFK", city="New York", timezone="EST"
            ),
            Airport(
                name="Los Angeles Intl", code="LAX", city="Los Angeles", timezone="PST"
            ),
            Airport(name="Heathrow", code="LHR", city="London", timezone="GMT"),
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
                    scheduled_departure=datetime(2026, 5, 20) + timedelta(days=day),
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
            User(name="Alice Smith", email="alice@test.com", password="hash123_secure"),
            User(name="Bob Jones", email="bob@test.com", password="hash456_secure"),
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


if __name__ == "__main__":
    populate_sample_data()
