import threading
from src.tickets.ticket_service import TicketService
import time


def test_isolation_without_lock(user_a_id, user_b_id, target_seat_id):
    """Test parallel execution leads to double-booking"""
    results = []
    start_event = threading.Event()

    def attempt_booking(user_id):
        start_event.wait()
        print(f"User {user_id} attempting to book seat {target_seat_id}...")
        result = TicketService.purchase_ticket_without_lock(
            user_id, target_seat_id)
        results.append(result)

    thread1 = threading.Thread(target=attempt_booking, args=(user_a_id,))
    thread2 = threading.Thread(target=attempt_booking, args=(user_b_id,))
    thread3 = threading.Thread(target=attempt_booking, args=(user_b_id,))

    thread1.start()
    thread2.start()
    thread3.start()

    time.sleep(0.1)
    start_event.set()

    thread1.join()
    thread2.join()
    thread3.join()

    successes = [r for r in results if r is not None]
    print("==============================")
    print("\n--- Isolation Test (WITHOUT LOCK) ---")
    print(f"Total attempts: 3")
    print(f"Successful bookings: {len(successes)}")

    if len(successes) >= 2:
        print("❌ RACE CONDITION DETECTED: System allowed multiple bookings for one seat!")
    elif len(successes) == 1:
        print("⚠️  Only 1 booking succeeded - race condition not triggered in this run")
    else:
        print("⚠️  Both bookings failed - check logs for database errors")

    print("==============================\n")


def test_isolation_forced_race_condition(user_a_id, user_b_id, target_seat_id):
    """
    FORCES the race condition by:
    1. Having all threads check availability simultaneously
    2. Pausing before the actual booking to maximize window
    """
    results = []
    barrier = threading.Barrier(3)

    def attempt_booking_with_forced_delay(user_id, thread_num):
        barrier.wait()
        time.sleep(0.001)

        print(
            f"[Thread {thread_num}] Attempting booking for User {user_id}...")
        result = TicketService.purchase_ticket_without_lock(
            user_id, target_seat_id)
        results.append((user_id, result))
        return result

    threads = [
        threading.Thread(
            target=attempt_booking_with_forced_delay, args=(user_a_id, 1)),
        threading.Thread(
            target=attempt_booking_with_forced_delay, args=(user_b_id, 2)),
        threading.Thread(
            target=attempt_booking_with_forced_delay, args=(user_b_id, 3)),
    ]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    successes = [r for r in results if r is not None and r is True]

    print("\n" + "=" * 50)
    print("--- FORCED RACE CONDITION TEST ---")
    print("=" * 50)
    print(f"Successful bookings: {len(successes)}")

    if len(successes) >= 2:
        print("❌ RACE CONDITION DETECTED (FORCED)!")
    else:
        print("⚠️  Race condition not triggered")
    print("=" * 50 + "\n")

    return len(successes) >= 2


def test_isolation_with_lock(user_a_id, user_b_id, target_seat_id):
    """Test parallel execution leads to preventing double-booking"""
    results = []

    def attempt_booking(user_id):
        print(f"User {user_id} attempting to book seat {target_seat_id}...")
        result = TicketService.purchase_ticket_with_lock(
            user_id, target_seat_id)
        results.append(result)

    thread1 = threading.Thread(target=attempt_booking, args=(user_a_id,))
    thread2 = threading.Thread(target=attempt_booking, args=(user_b_id,))

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()

    successes = [r for r in results if r is not None]
    print("==============================")
    print("\n--- Isolation Test (WITH LOCK) ---")
    print(f"Total attempts: 2")
    print(f"Successful bookings: {len(successes)}")

    if len(successes) == 1:
        print("✅ PASS: System prevented double-booking with FOR UPDATE lock!")
    elif len(successes) == 2:
        print("❌ FAIL: Lock failed - system still allowed multiple bookings!")
    else:
        print("⚠️  Both bookings failed - check logs for database errors")

    print("==============================\n")
