import os
import redis.asyncio as redis
import asyncio

from src.tickets.hybrid_ops import run_hybrid_ingestion_test, run_hybrid_update_rps_test
from src.tickets.redis_ops import run_pipelined_rps_test, run_pipelined_update_rps_test
from test.tickets.isolation_test import run_isolation_test_forced_race_condition, run_isolation_test_with_lock, run_isolation_test_without_lock
from test.users.performance_test import run_performance_test, run_concurrent_performance_test
from src.database import init_db
from src.users.postgres_ops import truncate_users
from src.tickets.postgres_ops import sync_seats_from_redis

REDIS_URL = os.getenv("REDIS_URL", "")
r = redis.from_url(REDIS_URL, decode_responses=False)


async def amain():
    print("Starting async performance tests...")
    # --- Task 1-2: Insert Performance Tests ---
    # try:
    #     await run_pipelined_rps_test(r, 30000)
    #     # --- Starting Pipelined Performance Test (30000 records) ---
    #     # FINISHED: 30000 operations in 10.94s
    #     # >>> MEASURED THROUGHPUT: 2741.56 RPS
    # finally:
    #     await r.aclose()

    # try:
    #     await run_hybrid_ingestion_test(r, 10000)
    #     # --- Starting Hybrid Ingestion Test (10000 operations) ---
    #     # REDIS INGESTION: 10000 ops in 1.61s
    #     # >>> MEASURED THROUGHPUT: 6227.27 RPS
    # finally:
    #     await r.aclose()

    # --- Task 3-4: Update Performance Tests ---
    try:
        results = await run_pipelined_update_rps_test(r, seat_count=5000, user_count=1000)
        print(f"Update RPS: {results['rps']:.2f}")
    finally:
        await r.aclose()

    # try:
    #     results = await run_hybrid_update_rps_test(r, seat_count=5000, user_count=1000)
    #     await sync_seats_from_redis(r)
    # finally:
    #     await r.aclose()


def main():
    print("Starting performance tests...")
    # Initialize database tables
    # init_db()
    # print("Database initialized successfully!")

    # truncate_users()
    # run_performance_test(1000)
    # ==============================
    # --- Performance Results ---
    # Total time for 1000 records: 137.28 seconds
    # Avg time per record: 137.28 ms
    # Throughput: 7.28 users/sec
    # ==============================
    # ==============================

    # truncate_users()
    # run_concurrent_performance_test(1000)
    # ==============================
    # --- Concurrent Performance Results ---
    # Total time for 1000 records: 122.58 seconds
    # Avg time per record: 122.58 ms
    # Throughput: 8.16 users/sec
    # ==============================
    # ==============================

    # run_isolation_test_without_lock(user_a_id=1, user_b_id=2, target_seat_id=12)
    # run_isolation_test_with_lock(user_a_id=1, user_b_id=2, target_seat_id=4)
    # run_isolation_test_forced_race_condition(user_a_id=1, user_b_id=2, target_seat_id=10)


if __name__ == "__main__":
    main()
    # asyncio.run(amain())
