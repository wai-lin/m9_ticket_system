import redis.asyncio as redis
import time


async def insert_seats_hybrid(r: redis.Redis, count: int) -> float:
    """
    Task 1-2: Hybrid insert - high RPS with sync marking.
    Returns: RPS
    """
    print(f"\n--- Hybrid Insert Test ({count} operations) ---")

    data_list = [
        {"id": f"h_{i}", "user_id": "1",
            "seat_id": str(i % 100), "price": "450.0"}
        for i in range(count)
    ]

    start_time = time.perf_counter()

    pipe = r.pipeline(transaction=False)
    for item in data_list:
        key = f"sync_pending:ticket:{item['id']}"
        pipe.hset(key, mapping=item)
        pipe.sadd("tickets_to_sync", key)

    await pipe.execute()

    duration = time.perf_counter() - start_time
    rps = count / duration

    print(f"REDIS INGESTION: {count} ops in {duration:.2f}s")
    print(f">>> MEASURED THROUGHPUT: {rps:.2f} RPS")
    return rps


async def update_seats_hybrid(r: redis.Redis, seat_count: int, user_count: int) -> dict:
    """
    Task 3-4: Hybrid update - concurrent reservations with sync marking.
    Returns: dict with results
    """
    print(f"\n--- Hybrid Update Test ({seat_count} seats, {user_count} users) ---")

    # Pre-populate seats
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

    # Hybrid Lua script
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

    # Simulate reservations
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


async def sync_seats_to_postgres(r: redis.Redis, sync_key: str = 'seats_to_sync') -> int:
    """
    Sync reserved/confirmed seats from Redis to Postgres.
    Reads from sync set and persists to database.
    """
    from sqlmodel import Session
    from src.database import engine
    from src.models.main import Seat
    
    with Session(engine) as session:
        seats_to_sync = await r.smembers(sync_key)
        
        synced_count = 0
        for seat_key in seats_to_sync:
            seat_data = await r.hgetall(seat_key)
            if not seat_data:
                continue
                
            seat_id = int(seat_data.get(b'seat_id', b'0').decode())
            status = seat_data.get(b'status', b'available').decode()
            
            seat = session.get(Seat, seat_id)
            if seat:
                seat.status = status
                session.add(seat)
                synced_count += 1
        
        session.commit()
        
        if seats_to_sync:
            await r.delete(sync_key)
            
        print(f"Synced {synced_count} seats to Postgres")
        return synced_count
