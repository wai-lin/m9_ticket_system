import threading
import time
import uuid
from src.users.postgres_ops import create_user
import asyncio
import redis.asyncio as redis
import os

from src.tickets.redis_ops import run_pipelined_update_rps_test
from src.tickets.hybrid_ops import run_hybrid_update_rps_test
from src.tickets.postgres_ops import sync_seats_from_redis


# --- Task 1-2: Insert Performance Tests ---

async def run_ticket_insert_performance_test(total_count: int = 30000):
    """
    Task 1-2: Test insert performance.
    """
    REDIS_URL = os.getenv("REDIS_URL", "")
    r = redis.from_url(REDIS_URL, decode_responses=False)
    
    try:
        from src.tickets.redis_ops import run_pipelined_rps_test
        rps = await run_pipelined_rps_test(r, total_count)
        return rps
    finally:
        await r.aclose()


# --- Task 3-4: Update Performance Tests ---

async def run_ticket_update_performance_test(seat_count: int = 5000, user_count: int = 1000):
    """
    Task 3-4: Test update (reservation) performance with Redis.
    Tracks success/failure for analytics.
    """
    REDIS_URL = os.getenv("REDIS_URL", "")
    r = redis.from_url(REDIS_URL, decode_responses=False)
    
    try:
        results = await run_pipelined_update_rps_test(r, seat_count, user_count)
        return results
    finally:
        await r.aclose()


async def run_ticket_hybrid_update_performance_test(seat_count: int = 5000, user_count: int = 1000):
    """
    Task 3-4: Test hybrid update performance (Redis + Postgres sync).
    Demonstrates the hybrid persistence pattern.
    """
    REDIS_URL = os.getenv("REDIS_URL", "")
    r = redis.from_url(REDIS_URL, decode_responses=False)
    
    try:
        results = await run_hybrid_update_rps_test(r, seat_count, user_count)
        
        # Sync to Postgres
        print("\n--- Syncing to Postgres ---")
        synced = await sync_seats_from_redis(r)
        
        return {
            **results,
            "synced_to_postgres": synced
        }
    finally:
        await r.aclose()


