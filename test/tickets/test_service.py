import asyncio
from src.tickets.ticket_cache import insert_seats_pipelined, update_seats_pipelined


async def test_ticket_insert_performance(total_count: int = 30000):
    """Test insert performance with Redis pipelining"""
    rps = await insert_seats_pipelined(total_count)
    return rps


async def test_ticket_update_performance(seat_count: int = 5000, user_count: int = 1000):
    """Test update performance with Redis seat updates"""
    results = await update_seats_pipelined(seat_count, user_count)
    return results


