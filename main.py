import asyncio

# User operations
from src.users.user_service import UserService

# Ticket operations
from src.tickets.ticket_service import TicketService

# Tests
from test.users.test_service import test_user_insert_performance, test_user_concurrent_performance
from test.tickets.test_service import test_ticket_insert_performance, test_ticket_update_performance, test_high_traffic_purchasing
from test.tickets.test_isolation import test_isolation_with_lock, test_isolation_without_lock, test_isolation_forced_race_condition

# Database
from src.database import init_db
from src.seed import run_seeder


# ===== Setup & Cleanup =====

async def setup_for_oltp_tests():
    """Setup: Clear database for OLTP tests"""
    print("\n[Setup] Clearing users and tickets...")
    UserService.truncate_users()
    TicketService.truncate_tickets()
    await TicketService.clear_redis_cache()
    print("[Setup] Database cleared.")

    print("[Setup] Creating flight infrastructure...")
    instance_id, first_seat_id = run_seeder()
    print(f"[Setup] Flight ready (ID: {instance_id} ... 100 seats).\n")
    return instance_id, first_seat_id


async def setup_for_high_traffic_tests():
    """Setup: Clear database for high-traffic tests"""
    print("\n[Setup] Clearing database for high-traffic test...")
    UserService.truncate_users()
    TicketService.truncate_tickets()
    await TicketService.clear_redis_cache()
    print("[Setup] Database cleared.")

    print("[Setup] Creating flight infrastructure...")
    instance_id, first_seat_id = run_seeder()
    print(f"[Setup] Flight ready (ID: {instance_id} ... 100 seats).")

    # Pre-create users for the test (required for Payment foreign key)
    print("[Setup] Creating test users...")
    for user_id in range(1, 1001):  # Create 1000 users
        UserService.create_user(f"user{user_id}", f"user{user_id}@test.com")
    print(f"[Setup] Created 1000 test users.\n")

    return instance_id, first_seat_id


async def task2_test1_sync_user_insert():
    """Test 1: Synchronous user insert"""
    print("\n" + "="*60)
    print("TASK 2 - Test 1: Synchronous User Insert")
    print("="*60)

    instance_id, first_seat_id = await setup_for_oltp_tests()
    rps = test_user_insert_performance(100)
    print(f"✓ Sequential Insert Complete: {rps:.2f} users/sec\n")


async def task2_test2_concurrent_user_insert():
    """Test 2: Concurrent user insert"""
    print("\n" + "="*60)
    print("TASK 2 - Test 2: Concurrent User Insert")
    print("="*60)

    instance_id, first_seat_id = await setup_for_oltp_tests()
    rps = test_user_concurrent_performance(100)
    print(f"✓ Concurrent Insert Complete: {rps:.2f} users/sec\n")


async def task2_test3_race_condition():
    """Test 3: Race condition demonstration"""
    print("\n" + "="*60)
    print("TASK 2 - Test 3: Race Condition (Without Lock)")
    print("="*60)

    instance_id, first_seat_id = await setup_for_oltp_tests()

    # Create 3 users for the race condition test
    u1 = UserService.create_user("User 1", "user1@test.com")
    u2 = UserService.create_user("User 2", "user2@test.com")
    u3 = UserService.create_user("User 3", "user3@test.com")

    print(f"✓ Created 3 users (IDs: {u1.id}, {u2.id}, {u3.id})")
    print("✓ Attempting 3 concurrent bookings for same seat...\n")

    test_isolation_without_lock(u1.id, u2.id, u3.id, first_seat_id)


async def task2_test4_lock_solution():
    """Test 4: Lock-based race condition prevention"""
    print("\n" + "="*60)
    print("TASK 2 - Test 4: Race Condition Prevention (With Lock)")
    print("="*60)

    instance_id, first_seat_id = await setup_for_oltp_tests()

    u1 = UserService.create_user("User A", "userA@test.com")
    u2 = UserService.create_user("User B", "userB@test.com")

    print(f"✓ Created 2 users (IDs: {u1.id}, {u2.id})")
    print("✓ Attempting 2 concurrent bookings for same seat (with FOR UPDATE lock)...\n")

    test_isolation_with_lock(u1.id, u2.id, first_seat_id)


# ===== TASK 3: High-RPS Redis Tests =====

async def task3_test1_insert_performance():
    """Test 1: Redis insert performance"""
    print("\n" + "="*60)
    print("TASK 3 - Test 1: Redis Insert Performance")
    print("="*60 + "\n")

    instance_id, first_seat_id = await setup_for_high_traffic_tests()
    rps = await test_ticket_insert_performance(30000)
    print(f"✓ Insert Test Complete: {rps:.2f} RPS\n")


async def task3_test2_update_performance():
    """Test 2: Redis update performance"""
    print("\n" + "="*60)
    print("TASK 3 - Test 2: Redis Update Performance")
    print("="*60 + "\n")

    instance_id, first_seat_id = await setup_for_high_traffic_tests()
    results = await test_ticket_update_performance(5000, 1000)
    print(f"✓ Update Test Complete: {results['rps']:.2f} RPS\n")


async def task3_test3_high_traffic():
    """Test 3: High-traffic ticket purchasing (Postgres + Redis)"""
    print("\n" + "="*60)
    print("Test 3: High-Traffic Ticket Purchasing")
    print("Write-through pattern: Postgres (authoritative) + Redis (cache)")
    print("="*60)

    instance_id, first_seat_id = await setup_for_high_traffic_tests()
    results = await test_high_traffic_purchasing(instance_id=instance_id, num_users=1000, seats_available=100)
    print(
        f"✓ High-Traffic Test Complete: {results['throughput']:.2f} purchases/sec\n")


async def run_task3_tests():
    """Run all Task 3 tests"""
    await task3_test1_insert_performance()
    await task3_test2_update_performance()
    await task3_test3_high_traffic()


async def main():
    """Main entry point"""

    print("\n" + "="*60)
    print("TICKET SYSTEM")
    print("="*60)

    # init_db()

    # TASK 2: OLTP Tests
    # await task2_test1_sync_user_insert()
    # await task2_test2_concurrent_user_insert()
    # await task2_test3_race_condition()
    # await task2_test4_lock_solution()

    # TASK 3: High-RPS & Caching Tests
    await run_task3_tests()
    # await task3_test3_high_traffic()

    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
