import threading
import time
import uuid
from src.users.user_service import UserService


def test_create_user():
    """Unit test for user creation"""
    user = UserService.create_user(
        name="Test User",
        email=f"test_{uuid.uuid4()}@test.com",
        password="password123"
    )
    assert user is not None
    assert user.name == "Test User"
    print("✓ User creation test passed")


def test_user_insert_performance(n=1000):
    """Performance test for user creation"""
    print(f"Starting performance test: Creating {n} users...")
    start_time = time.time()

    for i in range(n):
        UserService.create_user(
            name=f"Performance User {i}",
            email=f"perf_{i}_{time.time()}@test.com",
            password="password123"
        )

    end_time = time.time()
    total_time = end_time - start_time
    rps = n / total_time

    print("==============================")
    print(f"--- User Insert Performance ---")
    print(f"Total time for {n} records: {total_time:.2f} seconds")
    print(f"Avg time per record: {(total_time/n)*1000:.2f} ms")
    print(f"Throughput: {rps:.2f} users/sec")
    print("==============================")

    return rps


def test_user_concurrent_performance(n=1000):
    """Concurrent performance test for user creation"""
    print(f"Starting concurrent performance test: Creating {n} users...")

    def create_user_thread(start, end):
        for i in range(start, end):
            UserService.create_user(
                name=f"Performance User {i}",
                email=f"perf_{uuid.uuid4()}@test.com",
                password="password123"
            )

    start_time = time.time()

    per_n = n // 3
    thread1 = threading.Thread(target=create_user_thread, args=(0, per_n))
    thread2 = threading.Thread(
        target=create_user_thread, args=(per_n, 2 * per_n))
    thread3 = threading.Thread(target=create_user_thread, args=(2 * per_n, n))

    thread1.start()
    thread2.start()
    thread3.start()

    thread1.join()
    thread2.join()
    thread3.join()

    end_time = time.time()
    total_time = end_time - start_time
    rps = n / total_time

    print("==============================")
    print(f"--- Concurrent User Performance ---")
    print(f"Total time for {n} records: {total_time:.2f} seconds")
    print(f"Avg time per record: {(total_time/n)*1000:.2f} ms")
    print(f"Throughput: {rps:.2f} users/sec")
    print("==============================")

    return rps
