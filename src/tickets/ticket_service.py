from sqlmodel import Session, select, text
from src.models import Ticket, Seat, Payment, PaymentTicket
from src.database import engine
from src.redis import get_redis
import time


class TicketService:
    """Ticket operations (data access layer)"""

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

    @staticmethod
    async def purchase_with_redis_cache(user_id: int, seat_id: int) -> dict:
        """
        High-traffic ticket purchase: Write-through pattern.
        1. Purchase ticket in Postgres (authoritative with locks)
        2. Cache result in Redis (for fast reads)
        
        Returns: {success: bool, ticket_id: int, cached: bool}
        """
        
        # Step 1: Write to Postgres with lock (authoritative)
        ticket = TicketService.purchase_ticket_with_lock(user_id, seat_id)
        
        if not ticket:
            return {"success": False, "ticket_id": None, "cached": False}
        
        # Step 2: Update Redis cache asynchronously
        try:
            r = await get_redis()
            await r.hset(f"ticket:{ticket.id}", mapping={
                "user_id": str(user_id),
                "seat_id": str(seat_id),
                "status": "confirmed",
                "synced": "true"
            })
            await r.aclose()
            cached = True
        except Exception:
            cached = False  # Cache failure doesn't fail the purchase
        
        return {
            "success": True,
            "ticket_id": ticket.id,
            "cached": cached
        }

    @staticmethod
    def truncate_tickets() -> None:
        """Truncate all tickets and related data"""
        with Session(engine) as session:
            try:
                # Delete all payment-ticket links first (foreign key constraint)
                session.exec(text("DELETE FROM public.payment_ticket"))
                session.commit()
            except Exception:
                session.rollback()
            
            try:
                # Delete all tickets
                session.exec(text("DELETE FROM public.ticket"))
                session.commit()
            except Exception:
                session.rollback()
            
            try:
                # Delete all payments
                session.exec(text("DELETE FROM public.payment"))
                session.commit()
            except Exception:
                session.rollback()
            
            try:
                # Reset seats to available
                session.exec(text("UPDATE public.seat SET status = 'available'"))
                session.commit()
            except Exception:
                session.rollback()

    @staticmethod
    async def clear_redis_cache() -> None:
        """Clear all ticket-related keys from Redis cache"""
        from src.redis import get_redis
        
        r = await get_redis()
        
        # Scan and delete all ticket and seat keys
        cursor = 0
        deleted = 0
        
        while True:
            cursor, keys = await r.scan(cursor, match="ticket:*", count=100)
            if keys:
                await r.delete(*keys)
                deleted += len(keys)
            if cursor == 0:
                break
        
        # Also clear seat cache
        cursor = 0
        while True:
            cursor, keys = await r.scan(cursor, match="seat:*", count=100)
            if keys:
                await r.delete(*keys)
                deleted += len(keys)
            if cursor == 0:
                break
        
        await r.aclose()
        print(f"Cleared {deleted} keys from Redis cache")
