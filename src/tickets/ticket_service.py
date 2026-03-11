from src.tickets.ticket_repository import TicketRepository


class TicketService:
    """Business logic for Ticket operations"""

    def __init__(self):
        self.repository = TicketRepository()

    def get_available_seats(self, instance_id: int):
        """Get available seats"""
        return self.repository.get_available_seats(instance_id)

    def purchase_ticket_without_lock(self, user_id: int, seat_id: int):
        """Purchase ticket without lock (races possible)"""
        return self.repository.purchase_ticket_without_lock(user_id, seat_id)

    def purchase_ticket_with_lock(self, user_id: int, seat_id: int):
        """Purchase ticket with lock (race-condition safe)"""
        return self.repository.purchase_ticket_with_lock(user_id, seat_id)

    def cancel_booking(self, ticket_id: int):
        """Cancel a booking"""
        return self.repository.cancel_booking(ticket_id)


# Singleton instance
_ticket_service = TicketService()


# Convenience functions
def get_available_seats(instance_id: int):
    return _ticket_service.get_available_seats(instance_id)


def purchase_ticket_without_lock(user_id: int, seat_id: int):
    return _ticket_service.purchase_ticket_without_lock(user_id, seat_id)


def purchase_ticket_with_lock(user_id: int, seat_id: int):
    return _ticket_service.purchase_ticket_with_lock(user_id, seat_id)


def cancel_booking(ticket_id: int):
    return _ticket_service.cancel_booking(ticket_id)
