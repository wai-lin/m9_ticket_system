# Simplified Ticket System Architecture

## Overview
This is a minimal ticket booking system demonstrating:
- **Task 2 (OLTP)**: Atomic database operations with race condition prevention
- **Task 3 (High-RPS Redis)**: Simple Redis insert/update operations for performance testing

## File Structure

```
src/
├── database.py              # Database connection and schema setup
├── models/
│   └── main.py             # SQLModel data models (User, Ticket, Seat, Payment, PaymentTicket)
├── seed.py                 # Database seeding utilities
├── users/
│   ├── user_repository.py  # Data access layer for users
│   └── user_service.py     # Business logic for user operations
└── tickets/
    ├── ticket_repository.py # Data access layer for tickets
    ├── ticket_service.py    # Business logic for ticket operations
    └── ticket_cache.py      # Redis operations (simple insert/update)

test/
├── users/
│   └── test_service.py     # User performance tests
└── tickets/
    ├── test_isolation.py   # Race condition & lock tests
    └── test_service.py     # Redis performance tests

main.py                      # Entry point with test runners
```

## Core Components

### TASK 2: OLTP Operations (Postgres)

**User Service** (`src/users/user_service.py`)
- `create_user(name, email, password)` - Create a new user
- `truncate_users()` - Clear all users (for test setup)

**Ticket Service** (`src/tickets/ticket_service.py`)
- `get_available_seats(instance_id)` - List available seats
- `purchase_ticket_without_lock(user_id, seat_id)` - Vulnerable to race conditions
- `purchase_ticket_with_lock(user_id, seat_id)` - Uses FOR UPDATE to prevent races
- `cancel_booking(ticket_id)` - Cancel and refund a ticket

### TASK 3: High-RPS Redis Operations

**Ticket Cache** (`src/tickets/ticket_cache.py`)
- `insert_seats_pipelined(r, total_count)` - Batch insert seats to Redis
- `update_seats_pipelined(r, seat_count, user_count)` - Batch update seat statuses

## TASK 2 Tests (Concurrency & Race Conditions)

Run via `main.py` - uncomment test functions to execute:

**Test 1: Synchronous User Insert**
```python
task2_test1_sync_user_insert()  # Creates 100 users sequentially
```

**Test 2: Concurrent User Insert**
```python
task2_test2_concurrent_user_insert()  # Creates 100 users with 3 threads
```

**Test 3: Race Condition Demo**
```python
task2_test3_race_condition()  # Shows double-booking without lock
```

**Test 4: Lock Solution**
```python
task2_test4_lock_solution()  # Prevents double-booking with FOR UPDATE
```

## TASK 3 Tests (Redis Performance)

**Test 1: Insert Performance**
```python
asyncio.run(task3_test1_insert_performance())  # Pipelined insert of 30k records
```

**Test 2: Update Performance**
```python
asyncio.run(task3_test2_update_performance())  # Concurrent updates of 5k seats
```

## Design Principles

1. **Minimal Complexity**: No Lua scripts, no hybrid patterns - just simple operations
2. **Static Methods**: All service methods are static for cleaner API
3. **Layered Architecture**: Repository pattern (data access) + Service (business logic)
4. **Testing Focus**: Easy-to-run, isolated test functions

## Technology Stack

- **Database**: PostgreSQL (AWS RDS)
- **Cache/NoSQL**: Redis (RedisLabs)
- **ORM**: SQLModel (SQLAlchemy wrapper)
- **Async**: asyncio with redis-py
- **Testing**: Python's threading module

## How to Run Tests

```bash
# Configure environment variables
export SQLMODEL_URL="postgresql://..."
export REDIS_URL="redis://..."

# Run main.py to see available tests
uv run main.py

# Edit main.py and uncomment desired tests, then:
uv run main.py
```
