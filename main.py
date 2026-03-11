import os
import redis.asyncio as redis
import asyncio

from src.hybrid_operation import run_hybrid_ingestion_test
from src.redis_operation import run_pipelined_rps_test
from test.isolation_test import run_isolation_test_forced_race_condition, run_isolation_test_with_lock, run_isolation_test_without_lock
from test.performance_test import run_performance_test, run_concurrent_performance_test
from src.database import init_db
from src.operation import truncate_users

REDIS_URL = os.getenv("REDIS_URL", "")
r = redis.from_url(REDIS_URL, decode_responses=False)


async def amain():
    print("Starting async performance tests...")
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
