import time
import redis.asyncio as redis
from src.redis import get_redis


async def insert_seats_pipelined(total_count: int, chunk_size: int = 1000) -> float:
    """
    Insert performance test with pipelining.
    Returns: RPS (requests per second)
    """
    r = await get_redis()

    print(f"Inserting {total_count} seats to Redis with chunking {chunk_size}...")

    try:
        data_list = [{"id": f"p_{i}", "user_id": "-1", "status": "available", "price": "450"}
                     for i in range(total_count)]

        start_time = time.perf_counter()

        for i in range(0, total_count, chunk_size):
            chunk = data_list[i: i + chunk_size]
            pipe = r.pipeline(transaction=False)
            for item in chunk:
                key = f"ticket:{item['id']}"
                pipe.hset(key, mapping=item)
            await pipe.execute()

        duration = time.perf_counter() - start_time
        rps = total_count / duration
        print(f"FINISHED: {total_count} operations in {duration:.2f}s")
        print(f">>> MEASURED THROUGHPUT: {rps:.2f} RPS")
        return rps
    finally:
        await r.aclose()


async def update_seats_pipelined(seat_count: int, user_count: int) -> dict:
    """
    Update performance test - simple seat updates.
    Returns: dict with results
    """
    r = await get_redis()

    print(f"Updating {seat_count} seats to Redis for {user_count} users...")

    try:
        # Pre-populate seats
        start_populate = time.perf_counter()
        pipe = r.pipeline(transaction=False)
        for i in range(seat_count):
            seat_key = f"seat:{i}"
            pipe.hset(seat_key, mapping={
                "seat_id": str(i),
                "status": "available",
                "price": "450.0"
            })
        await pipe.execute()
        populate_time = time.perf_counter() - start_populate
        print(f"Populated {seat_count} seats in {populate_time:.2f}s")

        # Simulate simple updates
        start_update = time.perf_counter()
        pipe = r.pipeline(transaction=False)

        for user_id in range(user_count):
            seat_id = user_id % seat_count
            seat_key = f"seat:{seat_id}"
            pipe.hset(seat_key, mapping={
                "status": "occupied",
                "user_id": str(user_id)
            })

        await pipe.execute()

        update_duration = time.perf_counter() - start_update
        total_ops = user_count
        update_rps = total_ops / update_duration if update_duration > 0 else 0

        print(f"\nUpdated {total_ops} seats in {update_duration:.2f}s")
        print(f">>> MEASURED THROUGHPUT: {update_rps:.2f} RPS")

        return {
            "operations": total_ops,
            "duration": update_duration,
            "rps": update_rps
        }
    finally:
        await r.aclose()
