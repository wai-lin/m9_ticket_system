import os
import redis.asyncio as redis
import asyncio

# User operations
from src.users.user_service import create_user, truncate_users

# Ticket operations
from src.tickets.ticket_service import purchase_ticket_with_lock, purchase_ticket_without_lock, cancel_booking
from src.tickets.ticket_cache import insert_seats_pipelined, update_seats_pipelined
from src.tickets.ticket_sync import insert_seats_hybrid, update_seats_hybrid, sync_seats_to_postgres

# Tests
from test.users.test_service import test_user_insert_performance, test_user_concurrent_performance
from test.tickets.test_service import test_ticket_insert_performance, test_ticket_update_performance, test_ticket_hybrid_update_performance
from test.tickets.test_isolation import test_isolation_with_lock, test_isolation_without_lock, test_isolation_forced_race_condition

# Database
from src.database import init_db

REDIS_URL = os.getenv("REDIS_URL", "")


async def run_ticket_insert_tests():
    """Run Task 1-2: Insert performance tests"""
    print("\n" + "="*60)
    print("TASK 1-2: TICKET INSERT PERFORMANCE TESTS")
    print("="*60 + "\n")
    
    results = await test_ticket_insert_performance(30000)
    print(f"\n✓ Insert Performance: {results:.2f} RPS")


async def run_ticket_update_tests():
    """Run Task 3-4: Update performance tests"""
    print("\n" + "="*60)
    print("TASK 3-4: TICKET UPDATE PERFORMANCE TESTS")
    print("="*60 + "\n")
    
    results = await test_ticket_update_performance(5000, 1000)
    print(f"\n✓ Update Performance: {results['rps']:.2f} RPS")
    print(f"✓ Success Rate: {(results['successful']/(results['successful']+results['failed']))*100:.2f}%")


async def run_ticket_hybrid_tests():
    """Run hybrid insert and update tests with sync"""
    print("\n" + "="*60)
    print("HYBRID TESTS: REDIS + POSTGRES SYNC")
    print("="*60 + "\n")
    
    results = await test_ticket_hybrid_update_performance(5000, 1000)
    print(f"\n✓ Hybrid Update Performance: {results['rps']:.2f} RPS")
    print(f"✓ Synced to Postgres: {results['synced_to_postgres']} records")


def run_ticket_isolation_tests():
    """Run isolation tests"""
    print("\n" + "="*60)
    print("ISOLATION TESTS: RACE CONDITIONS")
    print("="*60 + "\n")
    
    print("\n--- Test 1: Without Lock (Should show race condition) ---")
    test_isolation_without_lock(user_a_id=1, user_b_id=2, target_seat_id=1)
    
    print("\n--- Test 2: Forced Race Condition ---")
    test_isolation_forced_race_condition(user_a_id=3, user_b_id=4, target_seat_id=2)
    
    print("\n--- Test 3: With Lock (Should prevent race condition) ---")
    test_isolation_with_lock(user_a_id=5, user_b_id=6, target_seat_id=3)


def run_user_performance_tests():
    """Run user creation performance tests"""
    print("\n" + "="*60)
    print("USER PERFORMANCE TESTS")
    print("="*60 + "\n")
    
    rps = test_user_insert_performance(100)
    print(f"\n✓ Sequential Insert: {rps:.2f} users/sec")
    
    rps = test_user_concurrent_performance(100)
    print(f"\n✓ Concurrent Insert: {rps:.2f} users/sec")


async def main_async():
    """Run all async tests"""
    try:
        await run_ticket_insert_tests()
    except Exception as e:
        print(f"Error in insert tests: {e}")
    
    try:
        await run_ticket_update_tests()
    except Exception as e:
        print(f"Error in update tests: {e}")
    
    try:
        await run_ticket_hybrid_tests()
    except Exception as e:
        print(f"Error in hybrid tests: {e}")


def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("TICKET SYSTEM TESTS")
    print("="*60)
    
    # Initialize database
    # init_db()
    # print("✓ Database initialized")
    
    # Run sync tests
    # run_user_performance_tests()
    # run_ticket_isolation_tests()
    
    # Run async tests
    # asyncio.run(main_async())
    
    print("\n✓ All tests available - uncomment in main() to run")


if __name__ == "__main__":
    main()



if __name__ == "__main__":
    main()
    # asyncio.run(amain())
