# Ticket Selling System

A minimal MVP demonstrating database transactions and resource contention.

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
    Seats ||--o{ Bookings: has_many
    Seats ||--|| Tickets: has_one
    Users ||--o{ Tickets: has_many
    Tickets ||--o{ Payments: has_one
    Airports {}
    Flights {}
    FlightInstances {}
    Seats {}
    Bookings {}
    Users {}
    Tickets {}
    Payments {}
```
