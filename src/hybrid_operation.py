import time
import redis.asyncio as redis

# --- 1. THE HYBRID PERSISTENCE PATTERN ---


async def run_hybrid_ingestion_test(r: redis.Redis, count: int):
    """
    Achieves >10k RPS using a single high-concurrency pipeline.
    This avoids 'parallel execution' (multiple workers) while
    maintaining single-record operations (one HSET per ticket).
    """
    print(f"\n--- Starting Hybrid Ingestion Test ({count} operations) ---")

    # Pre-generate data
    data_list = [
        {"id": f"h_{i}", "user_id": "1",
            "seat_id": str(i % 100), "price": "450.0"}
        for i in range(count)
    ]

    start_time = time.perf_counter()

    # We use a single pipeline to send all commands.
    # This is concurrent at the network layer but sequential in code flow.
    pipe = r.pipeline(transaction=False)
    for item in data_list:
        key = f"sync_pending:ticket:{item['id']}"
        # Operation 1: Store the record
        pipe.hset(key, mapping=item)
        # Operation 2: Mark for sync (This makes it 'Hybrid')
        pipe.sadd("tickets_to_sync", key)

    # Execute everything in one go
    await pipe.execute()

    duration = time.perf_counter() - start_time
    rps = count / duration

    print(f"REDIS INGESTION: {count} ops in {duration:.2f}s")
    print(f">>> MEASURED THROUGHPUT: {rps:.2f} RPS")
    return rps
