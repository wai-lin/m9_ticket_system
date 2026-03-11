# Simplified Ticket System - Quick Start Guide

## Project Status

✅ **Simplification Complete!**

This project has been refactored from an over-engineered solution to a minimal, clean implementation focusing on:

1. **Task 2 (OLTP)**: Transactional operations with race condition demonstration
2. **Task 3 (High-RPS Redis)**: Simple Redis performance testing

## What Was Removed

- ❌ All Lua scripts (no more complex atomic operations)
- ❌ Hybrid persistence patterns (no Redis-Postgres sync logic)
- ❌ Unnecessary schema files (User, Ticket)
- ❌ Verbose service patterns (replaced instance methods with static methods)
- ❌ Over-complicated test scenarios

## What Remains

✅ **Core OLTP Functions** (5 functions):
- `UserService.create_user()` - Create new user
- `UserService.truncate_users()` - Clear users for testing
- `TicketService.get_available_seats()` - List available seats
- `TicketService.purchase_ticket_without_lock()` - Vulnerable version (demonstrates race condition)
- `TicketService.purchase_ticket_with_lock()` - Safe version (uses FOR UPDATE)
- `TicketService.cancel_booking()` - Cancel a ticket

✅ **Core Redis Functions** (2 functions):
- `insert_seats_pipelined()` - Batch insert seats to Redis
- `update_seats_pipelined()` - Batch update seats in Redis

✅ **4 Simple Tests**:
1. Synchronous user insertion
2. Concurrent user insertion (3 threads)
3. Race condition demonstration (without lock)
4. Lock-based prevention (with FOR UPDATE)

## File Structure

```
src/
├── database.py                # DB connection setup
├── models/main.py             # SQLModel definitions
├── users/
│   ├── user_repository.py     # Data access (create, truncate)
│   └── user_service.py        # Business logic
└── tickets/
    ├── ticket_repository.py   # Data access (5 core functions)
    ├── ticket_service.py      # Business logic
    └── ticket_cache.py        # Redis operations (simple)

test/
├── users/test_service.py      # User tests
└── tickets/
    ├── test_isolation.py      # Race condition tests
    └── test_service.py        # Redis tests

main.py                         # Test runner
DESIGN.md                       # Architecture documentation
```

## How to Test

### Prerequisites

```bash
# Set environment variables in .env
export DB_HOST=your-rds-hostname
export DB_PORT=5432
export DB_USER=postgres
export DB_PASSWORD=your-password
export DB_NAME=ticket_system
export REDIS_URL=redis://your-redis-url
```

### Run Tests

Edit `main.py` and uncomment the test functions you want to run:

```python
# TASK 2: OLTP Tests
task2_test1_sync_user_insert()
task2_test2_concurrent_user_insert()
task2_test3_race_condition()
task2_test4_lock_solution()

# TASK 3: Redis Tests  
asyncio.run(task3_test1_insert_performance())
asyncio.run(task3_test2_update_performance())
```

Then execute:

```bash
uv run main.py
```

## Code Simplicity

- **Total Lines of Code**: ~600 lines (core logic)
- **Service Files**: 4 (user_service, user_repository, ticket_service, ticket_repository)
- **Cache File**: 1 (ticket_cache with 2 functions)
- **Test Files**: 3 with simple, isolated test functions

## Next Steps (Not Implemented Yet)

- Task 3: Simple Snowflake analytics pipeline
- Additional performance tuning
- Load testing with more concurrent users

---

**Last Updated**: After simplification refactor
**Status**: Ready for Task 2 Testing
