import threading
from src.operation import purchase_ticket_with_lock, purchase_ticket_without_lock


def run_isolation_test_without_lock(user_a_id, user_b_id, target_seat_id):
    """Test parallel execution leads to double-booking"""
    results = []

    def attempt_booking(user_id):
        # This will run in a separate thread
        print(f"User {user_id} attempting to book seat {target_seat_id}...")
        result = purchase_ticket_without_lock(user_id, target_seat_id)
        results.append(result)

    # Create two threads (simultaneous users)
    thread1 = threading.Thread(target=attempt_booking, args=(user_a_id,))
    thread2 = threading.Thread(target=attempt_booking, args=(user_b_id,))
    thread3 = threading.Thread(target=attempt_booking, args=(user_b_id,))

    # Start both at the same time
    thread1.start()
    thread2.start()
    thread3.start()

    # Wait for both to finish
    thread1.join()
    thread2.join()
    thread3.join()

    # Analyze results
    successes = [r for r in results if r is not None]
    print("==============================")
    print("\n--- Isolation Test Results (WITHOUT LOCK) ---")
    print(f"Total attempts: 3")
    print(f"Successful bookings: {len(successes)}")

    if len(successes) >= 2:
        print("❌ RACE CONDITION DETECTED: System allowed multiple bookings for one seat!")
    elif len(successes) == 1:
        print("⚠️  Only 1 booking succeeded - race condition not triggered in this run")
    else:
        print("⚠️  Both bookings failed - check logs for database errors")

    print("==============================")
    print("==============================")


def run_isolation_test_with_lock(user_a_id, user_b_id, target_seat_id):
    """Test parallel execution leads to preventing double-booking"""
    results = []

    def attempt_booking(user_id):
        # This will run in a separate thread
        print(f"User {user_id} attempting to book seat {target_seat_id}...")
        result = purchase_ticket_with_lock(user_id, target_seat_id)
        results.append(result)

    # Create two threads (simultaneous users)
    thread1 = threading.Thread(target=attempt_booking, args=(user_a_id,))
    thread2 = threading.Thread(target=attempt_booking, args=(user_b_id,))

    # Start both at the same time
    thread1.start()
    thread2.start()

    # Wait for both to finish
    thread1.join()
    thread2.join()

    # Analyze results
    successes = [r for r in results if r is not None]
    print("==============================")
    print("\n--- Isolation Test Results (WITH LOCK) ---")
    print(f"Total attempts: 2")
    print(f"Successful bookings: {len(successes)}")

    if len(successes) == 1:
        print("✅ PASS: System prevented double-booking with FOR UPDATE lock!")
    elif len(successes) == 2:
        print("❌ FAIL: Lock failed - system still allowed multiple bookings!")
    else:
        print("⚠️  Both bookings failed - check logs for database errors")

    print("==============================")
    print("==============================")
