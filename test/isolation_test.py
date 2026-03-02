import threading
from operation import purchase_ticket


def run_isolation_test(user_a_id, user_b_id, target_seat_id):
    """Requirement 6: Test if parallel execution leads to double-booking"""
    results = []

    def attempt_booking(user_id):
        # This will run in a separate thread
        print(f"User {user_id} attempting to book seat {target_seat_id}...")
        result = purchase_ticket(user_id, target_seat_id)
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

    print("\n--- Isolation Test Results ---")
    print(f"Total attempts: 2")
    print(f"Successful bookings: {len(successes)}")

    if len(successes) == 1:
        print("✅ PASS: System prevented double-booking.")
    else:
        print("❌ FAIL: System allowed multiple bookings for one seat!")