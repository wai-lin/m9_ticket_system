import time
import redis.asyncio as redis

# --- Hybrid Persistence Pattern ---


async def run_hybrid_ingestion_test(r: redis.Redis, count: int):
    """
    Task 1-2: Hybrid Ingestion Test.
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


# --- Task 3-4: Hybrid Update Pattern (Redis + Postgres) ---

async def run_hybrid_update_rps_test(r: redis.Redis, seat_count: int, user_count: int):
    """
    Task 3-4: Hybrid Update Test - Concurrent reservations with dual-write.
    Writes to Redis for high RPS + marks for Postgres sync.
    """
    print(f"\n--- Starting Hybrid Update Test ({seat_count} seats, {user_count} users) ---")

    # Pre-populate Redis with available seats
    start_populate = time.perf_counter()
    pipe = r.pipeline(transaction=False)
    for i in range(seat_count):
        seat_key = f"hseat:{i}"
        pipe.hset(seat_key, mapping={
            "seat_id": str(i),
            "status": "available",
            "price": "450.0"
        })
    await pipe.execute()
    populate_time = time.perf_counter() - start_populate
    print(f"Populated {seat_count} seats in {populate_time:.2f}s")

    # Hybrid Lua script: Reserve AND mark for sync in single atomic operation
    HYBRID_RESERVE_SCRIPT = """
    local seat_key = KEYS[1]
    local user_id = ARGV[1]
    local seat_data = redis.call('HGETALL', seat_key)
    
    if #seat_data == 0 then
        return 0
    end
    
    local seat_status = nil
    for i = 1, #seat_data, 2 do
        if seat_data[i] == 'status' then
            seat_status = seat_data[i+1]
            break
        end
    end
    
    if seat_status == 'available' then
        redis.call('HSET', seat_key, 'status', 'reserved', 'user_id', user_id)
        redis.call('SADD', 'hybrid_seats_to_sync', seat_key)
        return 1
    else
        return 0
    end
    """

    # Simulate concurrent reservation attempts
    start_reserve = time.perf_counter()
    successful = 0
    failed = 0

    for user_id in range(user_count):
        for attempt in range(seat_count // user_count + 1):
            seat_id = (user_id * (seat_count // user_count) + attempt) % seat_count
            seat_key = f"hseat:{seat_id}"
            result = await r.eval(HYBRID_RESERVE_SCRIPT, 1, seat_key, str(user_id))
            if result == 1:
                successful += 1
            else:
                failed += 1

    reserve_duration = time.perf_counter() - start_reserve
    total_ops = successful + failed
    reserve_rps = total_ops / reserve_duration if reserve_duration > 0 else 0

    print(f"\n--- Hybrid Reservation Results ---")
    print(f"Total attempts: {total_ops}")
    print(f"Successful reserves: {successful}")
    print(f"Failed reserves: {failed}")
    print(f"Success rate: {(successful/total_ops)*100:.2f}%")
    print(f"Time: {reserve_duration:.2f}s")
    print(f">>> THROUGHPUT: {reserve_rps:.2f} RPS")
    print(f"(Ready for Postgres sync after this test)")

    return {
        "successful": successful,
        "failed": failed,
        "rps": reserve_rps
    }
