from src.tickets.ticket_repository import TicketRepository
from src.models.main import Seat, Ticket


class TicketService:
    """Business logic for Ticket operations"""

    @staticmethod
    def get_available_seats(instance_id: int) -> list[Seat]:
        """Get available seats"""
        return TicketRepository.get_available_seats(instance_id)

    @staticmethod
    def purchase_ticket_without_lock(user_id: int, seat_id: int) -> Ticket:
        """Purchase ticket without lock (demonstrates race condition vulnerability)"""
        return TicketRepository.purchase_ticket_without_lock(user_id, seat_id)

    @staticmethod
    def purchase_ticket_with_lock(user_id: int, seat_id: int) -> Ticket:
        """Purchase ticket with lock (prevents race conditions)"""
        return TicketRepository.purchase_ticket_with_lock(user_id, seat_id)

    @staticmethod
    def cancel_booking(ticket_id: int) -> bool:
        """Cancel a booking"""
        return TicketRepository.cancel_booking(ticket_id)
