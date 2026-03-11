import time
import redis.asyncio as redis


async def run_pipelined_rps_test(r: redis.Redis, total_count: int, chunk_size: int = 1000):
    """
    Task 1-2: Insert Performance Test with Pipelining.
    To reach >10k RPS over a network, we use Pipelining.
    This sends 1,000 individual HSET commands in one TCP burst.
    """
    print(
        f"\n--- Starting Pipelined Performance Test ({total_count} records) ---")

    # Pre-generate all data
    data_list = [{"id": f"p_{i}", "u": "1", "s": "ok", "p": "450"}
                 for i in range(total_count)]

    start_time = time.perf_counter()

    # We process in large chunks (pipelines) to saturate the link
    # Each HSET is still a single record insert.
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
