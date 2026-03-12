"""SQLModel definitions for the ticket system"""
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


# ===== Airports =====
class Airport(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    code: str = Field(unique=True, index=True)
    city: str
    timezone: str

    # Tell SQLModel to use the departure_airport_id column for this list
    flights_departure: list["Flight"] = Relationship(
        back_populates="departure_airport",
        sa_relationship_kwargs={
            "primaryjoin": "Airport.id==Flight.departure_airport_id",
            "lazy": "selectin",
        },
    )
    # Tell SQLModel to use the arrival_airport_id column for this list
    flights_arrival: list["Flight"] = Relationship(
        back_populates="arrival_airport",
        sa_relationship_kwargs={
            "primaryjoin": "Airport.id==Flight.arrival_airport_id",
            "lazy": "selectin",
        },
    )


# ===== Flights =====
class Flight(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    flight_id: str = Field(unique=True, index=True)
    airline_code: str = Field(index=True)

    departure_airport_id: int = Field(foreign_key="airport.id")
    arrival_airport_id: int = Field(foreign_key="airport.id")

    # Explicitly link the back-references
    departure_airport: Airport = Relationship(
        back_populates="flights_departure",
        sa_relationship_kwargs={
            "foreign_keys": "[Flight.departure_airport_id]"},
    )
    arrival_airport: Airport = Relationship(
        back_populates="flights_arrival",
        sa_relationship_kwargs={"foreign_keys": "[Flight.arrival_airport_id]"},
    )

    flight_instances: list["FlightInstance"] = Relationship(
        back_populates="flight")


# ===== FlightInstances =====
class FlightInstance(SQLModel, table=True):
    """Specific flight instance (date/time)"""

    id: Optional[int] = Field(default=None, primary_key=True)
    flight_id: int = Field(foreign_key="flight.id")
    scheduled_departure: datetime = Field(index=True)
    actual_departure: Optional[datetime] = None
    base_price: float = Field(gt=0)

    # Relationships
    flight: Flight = Relationship(back_populates="flight_instances")
    seats: list["Seat"] = Relationship(back_populates="flight_instance")


# ===== Seats =====
class Seat(SQLModel, table=True):
    """Seat in a flight instance"""

    id: Optional[int] = Field(default=None, primary_key=True)
    instance_id: int = Field(foreign_key="flightinstance.id")
    seat_number: str = Field(index=True)
    class_: str = Field(alias="class")  # 'class' is reserved in Python
    status: str = Field(default="available")  # available, occupied, reserved

    # Relationships
    flight_instance: FlightInstance = Relationship(back_populates="seats")
    ticket: Optional["Ticket"] = Relationship(back_populates="seat")


# ===== Users =====
class User(SQLModel, table=True):
    """User information"""

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    email: str = Field(unique=True, index=True)
    password: str

    # Relationships
    tickets: list["Ticket"] = Relationship(back_populates="user")
    payments: list["Payment"] = Relationship(back_populates="user")


# ===== Tickets =====
class Ticket(SQLModel, table=True):
    """Ticket (booking)"""

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    seat_id: int = Field(foreign_key="seat.id")
    status: str = Field(default="pending")  # pending, confirmed, cancelled
    price: float = Field(gt=0)

    # Relationships
    user: User = Relationship(back_populates="tickets")
    seat: Seat = Relationship(back_populates="ticket")
    payment_tickets: list["PaymentTicket"] = Relationship(
        back_populates="ticket")


# ===== Payments =====
class Payment(SQLModel, table=True):
    """Payment record"""

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    total_price: float = Field(gt=0)
    purchased_date: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="pending")  # pending, completed, failed

    # Relationships
    user: User = Relationship(back_populates="payments")
    payment_tickets: list["PaymentTicket"] = Relationship(
        back_populates="payment")


# ===== PaymentTickets (Junction Table) =====
class PaymentTicket(SQLModel, table=True):
    """Junction table linking Payments to Tickets"""

    payment_id: int = Field(foreign_key="payment.id", primary_key=True)
    ticket_id: int = Field(foreign_key="ticket.id", primary_key=True)

    # Relationships
    payment: Payment = Relationship(back_populates="payment_tickets")
    ticket: Ticket = Relationship(back_populates="payment_tickets")
