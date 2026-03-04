from test.isolation_test import run_isolation_test_with_lock, run_isolation_test_without_lock
from test.performance_test import run_performance_test, run_concurrent_performance_test
from src.database import init_db
from src.operation import truncate_users


def main():
    # Initialize database tables
    init_db()
    print("Database initialized successfully!")



if __name__ == "__main__":
    main()

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

    run_isolation_test_without_lock(user_a_id=1, user_b_id=2, target_seat_id=5)

    # run_isolation_test_with_lock(user_a_id=1, user_b_id=2, target_seat_id=4)
