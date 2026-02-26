# Ticket Selling System

A minimal MVP demonstrating database transactions and resource contention.

## TeamMembers

- Wai Lin Aung
- Tom Everson

## Overview

Users compete to purchase tickets from a limited inventory. The system ensures data consistency through ACID transactions, preventing overselling and race conditions.

## Key Features

- **Limited Inventory**: Fixed ticket supply with concurrent purchase attempts
- **Transactions**: ACID-compliant operations to maintain consistency
- **Race Condition Handling**: Prevents double-booking through locking/serialization

```mermaid

erDiagram
    Airports ||--o{ Flights: has_many
    Flights ||--o{ FlightInstances: has_many
    FlightInstances ||--o{ Seats: has_many
    Seats ||--|| Tickets: has_one
    Users ||--o{ Tickets: has_many
    Tickets ||--o{ PaymentTikets: has_many
    Payments ||--o{ PaymentTikets: has_many
    Users ||--o{ Payments: has_many
    Airports {
        id int PK
        name string
        code string
        city string
        timezone string
    }
    Flights {
        id int PK
        flight_id string
        airline_code string
        depature_airport int FK
        arrival_airport int FK
    }
    FlightInstances {
        id int PK
        scheduled_depature timestampz
        actual_depature timestampz
        base_price decimal
    }
    Seats {
        id int PK
        instance_id int FK
        seat_number string
        class string
        status string
    }
    Users {
        id int PK
        name string
        email string
        password string
    }
    Tickets {
        id int PK
        user_id int FK
        seat_id int FK
        status string
        price decimal
    }
    PaymentTikets {
        payment_id int PK
        ticket_id int PK
    }
    Payments {
        id int PK
        user_id int FK
        total_price decimal
        purchased_date timestampz
        status string
    }
```
