from sqlmodel import Session, select
from models.main import User, Ticket, Seat, Payment, PaymentTicket
from src.database import engine


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
def purchase_ticket(user_id: int, seat_id: int):
    """
    Atomic operation: Reserves seat, creates ticket, and logs payment.
    If any step fails, the transaction rolls back.
    """
    with Session(engine) as session:
        try:
            # 1. Fetch seat and check availability
            seat = session.get(Seat, seat_id)
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
            session.commit()  # Commit here to get the ticket ID

            # 4. Create Payment record
            payment = Payment(user_id=user_id, total_price=450.0, status="completed")
            session.add(payment)
            session.commit()

            # 5. Link Payment to Ticket (Junction Table)
            link = PaymentTicket(payment_id=payment.id, ticket_id=new_ticket.id)
            session.add(link)

            session.commit()
            print(f"Successfully booked seat {seat.seat_number} for user {user_id}")
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
