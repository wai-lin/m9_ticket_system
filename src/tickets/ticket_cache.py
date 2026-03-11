import time
import redis.asyncio as redis


# --- Task 1-2: Insert with Pipelining ---

async def insert_seats_pipelined(r: redis.Redis, total_count: int, chunk_size: int = 1000) -> float:
    """
    Insert performance test with pipelining.
    Returns: RPS (requests per second)
    """
    print(f"\n--- Pipelined Insert Test ({total_count} records) ---")

    data_list = [{"id": f"p_{i}", "u": "1", "s": "ok", "p": "450"}
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


# --- Task 3-4: Update/Reserve with Lua Scripts ---

RESERVE_SEAT_SCRIPT = """
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

CONFIRM_RESERVATION_SCRIPT = """
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


async def reserve_seat(r: redis.Redis, seat_id: int, user_id: int) -> bool:
    """Atomically reserve a seat using Lua script"""
    seat_key = f"seat:{seat_id}"
    result = await r.eval(RESERVE_SEAT_SCRIPT, 1, seat_key, str(user_id))
    return result == 1


async def confirm_reservation(r: redis.Redis, seat_id: int, user_id: int) -> bool:
    """Confirm a reservation"""
    seat_key = f"seat:{seat_id}"
    result = await r.eval(CONFIRM_RESERVATION_SCRIPT, 1, seat_key, str(user_id))
    return result == 1


async def update_seats_pipelined(r: redis.Redis, seat_count: int, user_count: int) -> dict:
    """
    Update performance test - concurrent seat reservations.
    Returns: dict with results
    """
    print(f"\n--- Pipelined Update Test ({seat_count} seats, {user_count} users) ---")

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

    # Simulate reservations
    start_reserve = time.perf_counter()
    successful = 0
    failed = 0

    for user_id in range(user_count):
        for attempt in range(seat_count // user_count + 1):
            seat_id = (user_id * (seat_count // user_count) + attempt) % seat_count
            success = await reserve_seat(r, seat_id, user_id)
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
