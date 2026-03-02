import time
from models.main import User
from database import engine
from sqlmodel import Session

def run_performance_test(n=1000):
    """Requirement 5: Measure performance of creating N users"""
    print(f"Starting performance test: Creating {n} users...")
    start_time = time.time()

    with Session(engine) as session:
        for i in range(n):
            user = User(
                name=f"Performance User {i}",
                email=f"perf_{i}_{time.time()}@test.com", # Unique email
                password="password123"
            )
            session.add(user)
            # We commit in batches to balance speed and safety
            if i % 100 == 0:
                session.commit()
        session.commit()

    end_time = time.time()
    total_time = end_time - start_time
    print(f"--- Performance Results ---")
    print(f"Total time for {n} records: {total_time:.2f} seconds")
    print(f"Avg time per record: {(total_time/n)*1000:.2f} ms")
    print(f"Throughput: {n/total_time:.2f} users/sec")