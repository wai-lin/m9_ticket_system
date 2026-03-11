from sqlmodel import Session, select
from src.models.main import Ticket, Seat, Payment, PaymentTicket
from src.database import engine
import time


class TicketRepository:
    """Data access layer for Ticket operations"""

    @staticmethod
    def get_available_seats(instance_id: int) -> list[Seat]:
        """Get all available seats for a flight instance"""
        with Session(engine) as session:
            statement = select(Seat).where(
                Seat.instance_id == instance_id, Seat.status == "available"
            )
            return session.exec(statement).all()

    @staticmethod
    def get_seat(seat_id: int) -> Seat:
        """Get a specific seat"""
        with Session(engine) as session:
            return session.get(Seat, seat_id)

    @staticmethod
    def purchase_ticket_without_lock(user_id: int, seat_id: int):
        """Create ticket without lock (demonstrates race condition vulnerability)"""
        with Session(engine) as session:
            try:
                statement = select(Seat).where(Seat.id == seat_id)
                seat = session.exec(statement).first()
                
                if not seat or seat.status != "available":
                    raise Exception("Seat is no longer available.")

                # Simulate concurrency delay
                time.sleep(1)

                seat.status = "occupied"
                session.add(seat)

                new_ticket = Ticket(
                    user_id=user_id, seat_id=seat_id, price=450.0, status="confirmed"
                )
                session.add(new_ticket)

                payment = Payment(
                    user_id=user_id, total_price=450.0, status="completed")
                session.add(payment)

                link = PaymentTicket(payment=payment, ticket=new_ticket)
                session.add(link)

                session.commit()
                return new_ticket

            except Exception as e:
                session.rollback()
                return None

    @staticmethod
    def purchase_ticket_with_lock(user_id: int, seat_id: int):
        """Create ticket with FOR UPDATE lock (prevents race conditions)"""
        with Session(engine) as session:
            try:
                statement = select(Seat).where(
                    Seat.id == seat_id).with_for_update()
                seat = session.exec(statement).first()
                
                if not seat or seat.status != "available":
                    raise Exception("Seat is no longer available.")

                seat.status = "occupied"
                session.add(seat)

                new_ticket = Ticket(
                    user_id=user_id, seat_id=seat_id, price=450.0, status="confirmed"
                )
                session.add(new_ticket)

                payment = Payment(
                    user_id=user_id, total_price=450.0, status="completed")
                session.add(payment)

                link = PaymentTicket(payment=payment, ticket=new_ticket)
                session.add(link)

                session.commit()
                return new_ticket

            except Exception as e:
                session.rollback()
                return None

    @staticmethod
    def cancel_booking(ticket_id: int):
        """Cancel a ticket and free up the seat"""
        with Session(engine) as session:
            ticket = session.get(Ticket, ticket_id)
            if ticket:
                ticket.status = "cancelled"
                seat = session.get(Seat, ticket.seat_id)
                seat.status = "available"

                session.add(ticket)
                session.add(seat)
                session.commit()
                return True
            return False
