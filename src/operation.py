from sqlmodel import Session, select, text
from src.models.main import User, Ticket, Seat, Payment, PaymentTicket
from src.database import engine, DB_SCHEMA
import time


# --- Operation 1: Create a User ---
def create_user(name: str, email: str, password: str):
    with Session(engine) as session:
        new_user = User(name=name, email=email, password=password)
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return new_user


# --- Operation 2: Get Available Seats ---
def get_available_seats(instance_id: int):
    with Session(engine) as session:
        statement = select(Seat).where(
            Seat.instance_id == instance_id, Seat.status == "available"
        )
        return session.exec(statement).all()


# --- Operation 3: The Purchase Flow (Atomic) ---
def purchase_ticket_without_lock(user_id: int, seat_id: int):
    """
    Atomic operation WITHOUT lock: Demonstrates race condition vulnerability.
    Multiple users can book the same seat simultaneously.
    """
    with Session(engine) as session:
        try:
            # 1. Fetch seat WITHOUT lock - use fresh SELECT (not cached get)
            statement = select(Seat).where(Seat.id == seat_id)
            seat = session.exec(statement).first()
            if not seat or seat.status != "available":
                raise Exception("Seat is no longer available.")

            # 2. Update seat status
            seat.status = "occupied"
            session.add(seat)

            # 3. Create Ticket
            # In a real app, we'd calculate price based on FlightInstance + base_price
            new_ticket = Ticket(
                user_id=user_id, seat_id=seat_id, price=450.0, status="confirmed"
            )
            session.add(new_ticket)

            # 4. Create Payment record
            payment = Payment(
                user_id=user_id, total_price=450.0, status="completed")
            session.add(payment)

            # 5. Link Payment to Ticket (Junction Table)
            link = PaymentTicket(payment=payment, ticket=new_ticket)
            session.add(link)

            # Commit everything at once
            session.commit()
            print(
                f"Successfully booked seat {seat.seat_number} for user {user_id}")
            return new_ticket

        except Exception as e:
            session.rollback()  # Undo everything if an error occurs
            print(f"Booking failed: {e}")
            return None


# --- Operation 3: The Purchase Flow (Atomic) ---
def purchase_ticket_with_lock(user_id: int, seat_id: int):
    """
    Atomic operation: Reserves seat, creates ticket, and logs payment.
    If any step fails, the transaction rolls back.
    """
    with Session(engine) as session:
        try:
            # 1. Fetch seat with FOR UPDATE lock to prevent race conditions
            statement = select(Seat).where(
                Seat.id == seat_id).with_for_update()
            seat = session.exec(statement).first()
            if not seat or seat.status != "available":
                raise Exception("Seat is no longer available.")

            # 2. Update seat status
            seat.status = "occupied"
            session.add(seat)

            # 3. Create Ticket
            # In a real app, we'd calculate price based on FlightInstance + base_price
            new_ticket = Ticket(
                user_id=user_id, seat_id=seat_id, price=450.0, status="confirmed"
            )
            session.add(new_ticket)

            # 4. Create Payment record
            payment = Payment(
                user_id=user_id, total_price=450.0, status="completed")
            session.add(payment)

            # 5. Link Payment to Ticket (Junction Table)
            link = PaymentTicket(payment=payment, ticket=new_ticket)
            session.add(link)

            # Commit everything at once - ensures atomicity
            session.commit()
            print(
                f"Successfully booked seat {seat.seat_number} for user {user_id}")
            return new_ticket

        except Exception as e:
            session.rollback()  # Undo everything if an error occurs
            print(f"Booking failed: {e}")
            return None


# --- Operation 4: Cancel Booking ---
def cancel_booking(ticket_id: int):
    with Session(engine) as session:
        ticket = session.get(Ticket, ticket_id)
        if ticket:
            ticket.status = "cancelled"
            # Free up the seat
            seat = session.get(Seat, ticket.seat_id)
            seat.status = "available"

            session.add(ticket)
            session.add(seat)
            session.commit()
            return True
        return False


# --- Operation 5: Truncate User Table ---
def truncate_users():
    """Truncate user table and reset ID sequence to 1"""
    with Session(engine) as session:
        # Use raw SQL to truncate and reset sequence with schema prefix
        session.exec(
            text(f'TRUNCATE TABLE {DB_SCHEMA}."user" RESTART IDENTITY CASCADE'))
        session.commit()
        print("User table truncated and ID sequence reset to 1")
