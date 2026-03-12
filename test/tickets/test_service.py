import asyncio
import time
from src.tickets.ticket_cache import insert_seats_pipelined, update_seats_pipelined
from src.tickets.ticket_service import TicketService


async def test_ticket_insert_performance(total_count: int = 30000):
    """Test insert performance with Redis pipelining"""
    print(f"\n--- Pipelined Insert Test ({total_count:,} records) ---")
    rps = await insert_seats_pipelined(total_count)
    print(f">>> MEASURED THROUGHPUT: {rps:.2f} RPS")
    return rps


async def test_ticket_update_performance(seat_count: int = 5000, user_count: int = 1000):
    """Test update performance with Redis seat updates"""
    print(
        f"\n--- Pipelined Update Test ({seat_count:,} seats, {user_count:,} users) ---")
    results = await update_seats_pipelined(seat_count, user_count)
    print(f">>> MEASURED THROUGHPUT: {results['rps']:.2f} RPS")
    return results


async def test_high_traffic_purchasing(instance_id: int, num_users: int = 1000, seats_available: int = 100):
    """
    High-traffic ticket purchasing with Postgres + Redis.
    Real-world scenario: many users competing for limited seats.
    Demonstrates write-through pattern: authoritative DB + cache layer.

    Args:
        instance_id: Flight instance ID to purchase tickets from
        num_users: Number of concurrent users
        seats_available: Expected number of available seats
    """
    from sqlmodel import Session, select
    from src.models import Seat
    from src.database import engine

    # Get actual seat IDs from the database
    with Session(engine) as session:
        seats = session.exec(
            select(Seat).where(Seat.instance_id ==
                               instance_id).limit(seats_available)
        ).all()

    if not seats:
        print(f"❌ No seats found for instance {instance_id}")
        return {
            "succeeded": 0,
            "failed": num_users,
            "cached": 0,
            "throughput": 0,
            "duration": 0,
            "avg_latency_ms": 0
        }

    seat_ids = [s.id for s in seats]
    succeeded = 0
    failed = 0

    print(
        f"\n--- High-Traffic Purchasing Test ({num_users} users, {len(seat_ids)} seats) ---")
    print(f"🎫 Seat IDs: {seat_ids[:5]}{'...' if len(seat_ids) > 5 else ''}")

    start_time = time.perf_counter()

    # Concurrent purchasing with asyncio
    tasks = []
    for user_id in range(1, num_users + 1):
        seat_id = seat_ids[(user_id - 1) % len(seat_ids)]
        tasks.append(TicketService.purchase_with_redis_cache(user_id, seat_id))

    results = await asyncio.gather(*tasks, return_exceptions=True)

    cached_count = 0
    for result in results:
        if isinstance(result, dict) and result.get("success"):
            succeeded += 1
            if result.get("cached"):
                cached_count += 1
        else:
            failed += 1

    duration = time.perf_counter() - start_time
    throughput = succeeded / duration if duration > 0 else 0

    print("="*50)
    print("----- RESULTS -----")
    print(
        f"✓ Successful: {succeeded}/{num_users} ({(succeeded/(succeeded+failed))*100:.1f}%)")
    print(f"✗ Failed: {failed}/{num_users}")
    if succeeded > 0:
        print(f"Cached: {cached_count}/{succeeded}")
    print(f"Throughput: {throughput:.2f} purchases/sec")
    print(f"Duration: {duration:.2f}s")
    print(f"Avg latency: {(duration/num_users)*1000:.2f}ms")
    print("="*50)

    return {
        "succeeded": succeeded,
        "failed": failed,
        "cached": cached_count,
        "throughput": throughput,
        "duration": duration,
        "avg_latency_ms": (duration/num_users)*1000
    }
