import os
import asyncio
import redis.asyncio as redis

# User operations
from src.users.user_service import UserService

# Ticket operations
from src.tickets.ticket_service import TicketService

# Tests
from test.users.test_service import test_user_insert_performance, test_user_concurrent_performance
from test.tickets.test_service import test_ticket_insert_performance, test_ticket_update_performance
from test.tickets.test_isolation import test_isolation_with_lock, test_isolation_without_lock, test_isolation_forced_race_condition

# Database
from src.database import init_db

REDIS_URL = os.getenv("REDIS_URL", "")


# ===== TASK 2: OLTP Tests =====

def task2_test1_sync_user_insert():
    """Test 1: Synchronous user insert"""
    print("\n" + "="*60)
    print("TASK 2 - Test 1: Synchronous User Insert")
    print("="*60)
    
    UserService.truncate_users()
    rps = test_user_insert_performance(100)
    print(f"✓ Sequential Insert Complete: {rps:.2f} users/sec\n")


def task2_test2_concurrent_user_insert():
    """Test 2: Concurrent user insert"""
    print("\n" + "="*60)
    print("TASK 2 - Test 2: Concurrent User Insert")
    print("="*60)
    
    UserService.truncate_users()
    rps = test_user_concurrent_performance(100)
    print(f"✓ Concurrent Insert Complete: {rps:.2f} users/sec\n")


def task2_test3_race_condition():
    """Test 3: Race condition demonstration"""
    print("\n" + "="*60)
    print("TASK 2 - Test 3: Race Condition (Without Lock)")
    print("="*60)
    
    # Create 4 users and a flight instance first
    u1 = UserService.create_user("User 1", "user1@test.com")
    u2 = UserService.create_user("User 2", "user2@test.com")
    u3 = UserService.create_user("User 3", "user3@test.com")
    
    print(f"\n✓ Created 3 users (IDs: {u1.id}, {u2.id}, {u3.id})")
    print("✓ Attempting 3 concurrent bookings for same seat...\n")
    
    test_isolation_forced_race_condition(u1.id, u2.id, 1)


def task2_test4_lock_solution():
    """Test 4: Lock-based race condition prevention"""
    print("\n" + "="*60)
    print("TASK 2 - Test 4: Race Condition Prevention (With Lock)")
    print("="*60)
    
    u1 = UserService.create_user("User A", "userA@test.com")
    u2 = UserService.create_user("User B", "userB@test.com")
    
    print(f"\n✓ Created 2 users (IDs: {u1.id}, {u2.id})")
    print("✓ Attempting 2 concurrent bookings for same seat (with FOR UPDATE lock)...\n")
    
    test_isolation_with_lock(u1.id, u2.id, 2)


# ===== TASK 3: High-RPS Redis Tests =====

async def task3_test1_insert_performance():
    """Test 1: Redis insert performance"""
    print("\n" + "="*60)
    print("TASK 3 - Test 1: Redis Insert Performance")
    print("="*60 + "\n")
    
    rps = await test_ticket_insert_performance(30000)
    print(f"\n✓ Insert Test Complete: {rps:.2f} RPS\n")


async def task3_test2_update_performance():
    """Test 2: Redis update performance"""
    print("\n" + "="*60)
    print("TASK 3 - Test 2: Redis Update Performance")
    print("="*60 + "\n")
    
    results = await test_ticket_update_performance(5000, 1000)
    print(f"\n✓ Update Test Complete: {results['rps']:.2f} RPS\n")


async def run_task3_tests():
    """Run all Task 3 tests"""
    await task3_test1_insert_performance()
    await task3_test2_update_performance()


def main():
    """Main entry point"""
    
    print("\n" + "="*60)
    print("TICKET SYSTEM - SIMPLIFIED TESTS")
    print("="*60)
    
    # Uncomment the tests you want to run:
    
    # TASK 2: OLTP Tests
    # task2_test1_sync_user_insert()
    # task2_test2_concurrent_user_insert()
    # task2_test3_race_condition()
    # task2_test4_lock_solution()
    
    # TASK 3: Redis Tests
    # asyncio.run(run_task3_tests())
    
    print("\n✓ All tests are available. Uncomment in main() to run them.")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()

