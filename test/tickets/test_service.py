import asyncio
import os
import redis.asyncio as redis
from src.tickets.ticket_cache import insert_seats_pipelined, update_seats_pipelined


async def test_ticket_insert_performance(total_count: int = 30000):
    """Test insert performance with Redis pipelining"""
    REDIS_URL = os.getenv("REDIS_URL", "")
    r = redis.from_url(REDIS_URL, decode_responses=False)
    
    try:
        rps = await insert_seats_pipelined(r, total_count)
        return rps
    finally:
        await r.aclose()


async def test_ticket_update_performance(seat_count: int = 5000, user_count: int = 1000):
    """Test update performance with Redis seat updates"""
    REDIS_URL = os.getenv("REDIS_URL", "")
    r = redis.from_url(REDIS_URL, decode_responses=False)
    
    try:
        results = await update_seats_pipelined(r, seat_count, user_count)
        return results
    finally:
        await r.aclose()

