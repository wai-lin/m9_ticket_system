from sqlmodel import Session, select, text
from src.models.main import Ticket, Seat, Payment, PaymentTicket
from src.database import engine, DB_SCHEMA
import time


# --- Operation: Get Available Seats ---
def get_available_seats(instance_id: int):
    with Session(engine) as session:
        statement = select(Seat).where(
            Seat.instance_id == instance_id, Seat.status == "available"
        )
        return session.exec(statement).all()


# --- Operation: Purchase Ticket WITHOUT Lock (Demonstrates Race Condition) ---
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
            print(f"User {user_id} sees seat {seat_id} as {seat.status}")
            if not seat or seat.status != "available":
                raise Exception("Seat is no longer available.")

            # --- SIMULATE CONCURRENCY DELAY ---
            # This allows other threads to read 'available' before we commit 'occupied'
            print(f"User {user_id} detected seat {seat_id} is available. Pausing...")
            time.sleep(1)

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


# --- Operation: Purchase Ticket WITH Lock (Prevents Race Condition) ---
def purchase_ticket_with_lock(user_id: int, seat_id: int):
    """
    Atomic operation: Reserves seat, creates ticket, and logs payment.
    Uses FOR UPDATE lock to prevent race conditions.
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


# --- Operation: Cancel Booking ---
def cancel_booking(ticket_id: int):
    """Cancel a ticket and free up the associated seat."""
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
