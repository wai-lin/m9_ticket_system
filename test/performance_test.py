import time
from src.models.main import User
from src.database import engine
from sqlmodel import Session
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
