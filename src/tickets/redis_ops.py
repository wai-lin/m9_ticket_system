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


# --- Task 3-4: Atomic Seat Reservation (Update) Operations ---

# Lua script for atomic seat reservation (prevents race conditions at Redis level)
RESERVE_SEAT_SCRIPT = """
-- KEYS[1]: seat key (e.g., "seat:123")
-- ARGV[1]: user_id
-- Returns: 1 if reserved successfully, 0 if seat already taken
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
    redis.call('HSET', seat_key, 'status', 'reserved', 'user_id', user_id, 'reserved_at', tostring(redis.call('TIME')[1]))
    redis.call('SADD', 'seats_to_sync', seat_key)
    return 1
else
    return 0
end
"""

# Lua script for confirming reservation (final purchase)
CONFIRM_RESERVATION_SCRIPT = """
-- KEYS[1]: seat key
-- ARGV[1]: user_id
-- Returns: 1 if confirmed, 0 if reservation expired or user mismatch
local seat_key = KEYS[1]
local user_id = ARGV[1]
local seat_data = redis.call('HGETALL', seat_key)

if #seat_data == 0 then
    return 0
end

local seat_user = nil
local seat_status = nil
for i = 1, #seat_data, 2 do
    if seat_data[i] == 'user_id' then
        seat_user = seat_data[i+1]
    elseif seat_data[i] == 'status' then
        seat_status = seat_data[i+1]
    end
end

if seat_status == 'reserved' and seat_user == user_id then
    redis.call('HSET', seat_key, 'status', 'confirmed')
    redis.call('SADD', 'seats_to_sync', seat_key)
    return 1
else
    return 0
end
"""


async def reserve_seat_in_redis(r: redis.Redis, seat_id: int, user_id: int) -> bool:
    """
    Task 3-4: Atomically reserve a seat in Redis.
    Prevents double-booking using Lua script (true atomic operation).
    Returns True if reservation successful, False if seat already taken.
    """
    seat_key = f"seat:{seat_id}"
    result = await r.eval(RESERVE_SEAT_SCRIPT, 1, seat_key, str(user_id))
    return result == 1


async def confirm_reservation_in_redis(r: redis.Redis, seat_id: int, user_id: int) -> bool:
    """
    Task 3-4: Confirm a reservation (mark as fully purchased).
    Returns True if confirmed, False if reservation invalid/expired.
    """
    seat_key = f"seat:{seat_id}"
    result = await r.eval(CONFIRM_RESERVATION_SCRIPT, 1, seat_key, str(user_id))
    return result == 1


async def run_pipelined_update_rps_test(r: redis.Redis, seat_count: int, user_count: int):
    """
    Task 3-4: Update Performance Test - Concurrent seat reservations.
    Simulates many users trying to reserve available seats.
    Tracks success/failure for analytics.
    """
    print(f"\n--- Starting Pipelined Update Test ({seat_count} seats, {user_count} users) ---")

    # Pre-populate Redis with available seats
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

    # Simulate concurrent reservation attempts
    start_reserve = time.perf_counter()
    successful = 0
    failed = 0

    # Each user attempts to reserve a random seat multiple times
    for user_id in range(user_count):
        for attempt in range(seat_count // user_count + 1):
            seat_id = (user_id * (seat_count // user_count) + attempt) % seat_count
            success = await reserve_seat_in_redis(r, seat_id, user_id)
            if success:
                successful += 1
            else:
                failed += 1

    reserve_duration = time.perf_counter() - start_reserve
    total_ops = successful + failed
    reserve_rps = total_ops / reserve_duration if reserve_duration > 0 else 0

    print(f"\n--- Reservation Results ---")
    print(f"Total attempts: {total_ops}")
    print(f"Successful reserves: {successful}")
    print(f"Failed reserves: {failed}")
    print(f"Success rate: {(successful/total_ops)*100:.2f}%")
    print(f"Time: {reserve_duration:.2f}s")
    print(f">>> THROUGHPUT: {reserve_rps:.2f} RPS")

    return {
        "successful": successful,
        "failed": failed,
        "rps": reserve_rps
    }
