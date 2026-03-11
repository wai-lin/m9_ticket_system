import asyncio
import time
from src.tickets.ticket_cache import insert_seats_pipelined, update_seats_pipelined
from src.tickets.ticket_service import TicketService


async def test_ticket_insert_performance(total_count: int = 30000):
    """Test insert performance with Redis pipelining"""
    rps = await insert_seats_pipelined(total_count)
    return rps


async def test_ticket_update_performance(seat_count: int = 5000, user_count: int = 1000):
    """Test update performance with Redis seat updates"""
    results = await update_seats_pipelined(seat_count, user_count)
    return results


async def test_high_traffic_purchasing(num_users: int = 1000, seats_available: int = 100):
    """
    High-traffic ticket purchasing with Postgres + Redis.
    Real-world scenario: many users competing for limited seats.
    Demonstrates write-through pattern: authoritative DB + cache layer.
    """
    succeeded = 0
    failed = 0

    print(
        f"\n--- High-Traffic Purchasing Test ({num_users} users, {seats_available} seats) ---")

    start_time = time.perf_counter()

    # Concurrent purchasing with asyncio
    tasks = []
    for user_id in range(1, num_users + 1):
        seat_id = (user_id % seats_available) + 1
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

    print(f"Successful purchases: {succeeded}/{num_users}")
    print(f"Failed purchases: {failed}/{num_users}")
    print(f"Cached in Redis: {cached_count}/{succeeded}")
    print(f"Success rate: {(succeeded/(succeeded+failed))*100:.1f}%")
    print(f"Throughput: {throughput:.2f} purchases/sec")
    print(f"Duration: {duration:.2f}s")
    print(f"Avg latency: {(duration/num_users)*1000:.2f}ms per purchase")

    return {
        "succeeded": succeeded,
        "failed": failed,
        "cached": cached_count,
        "throughput": throughput,
        "duration": duration,
        "avg_latency_ms": (duration/num_users)*1000
    }
