import threading
import time
import uuid
from src.operation import create_user


def run_performance_test(n=1000):
    """Measure performance of creating N users"""
    print(f"Starting performance test: Creating {n} users...")
    start_time = time.time()

    for i in range(n):
        create_user(
            name=f"Performance User {i}",
            email=f"perf_{i}_{time.time()}@test.com",  # Unique email
            password="password123"
        )

    end_time = time.time()
    total_time = end_time - start_time
    print("==============================")
    print(f"--- Performance Results ---")
    print(f"Total time for {n} records: {total_time:.2f} seconds")
    print(f"Avg time per record: {(total_time/n)*1000:.2f} ms")
    print(f"Throughput: {n/total_time:.2f} users/sec")
    print("==============================")
    print("==============================")

def run_concurrent_performance_test(n=1000):
    """Measure performance of creating N users concurrently"""
    print(f"Starting concurrent performance test: Creating {n} users...")

    def create_user_thread(start, end):
        for i in range(start, end):
            create_user(
                name=f"Performance User {i}",
                email=f"perf_{uuid.uuid4()}@test.com",  # Guaranteed unique
                password="password123"
            )

    start_time = time.time()

    per_n = n // 3
    thread1 = threading.Thread(target=create_user_thread, args=(0, per_n))
    thread2 = threading.Thread(target=create_user_thread, args=(per_n, 2 * per_n))
    thread3 = threading.Thread(target=create_user_thread, args=(2 * per_n, n))

    thread1.start()
    thread2.start()
    thread3.start()

    thread1.join()
    thread2.join()
    thread3.join()

    end_time = time.time()
    total_time = end_time - start_time
    print("==============================")
    print(f"--- Concurrent Performance Results ---")
    print(f"Total time for {n} records: {total_time:.2f} seconds")
    print(f"Avg time per record: {(total_time/n)*1000:.2f} ms")
    print(f"Throughput: {n/total_time:.2f} users/sec")
    print("==============================")
    print("==============================")
