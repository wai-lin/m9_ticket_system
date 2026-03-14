"""Analytics data loader - Extract from PostgreSQL, load to Snowflake"""
import pandas as pd
from sqlmodel import Session, select, text
from src.database import engine
from src.models import User, Ticket, Payment, PaymentTicket, Seat, Flight, FlightInstance, Airport
from src.snowflake import get_snowflake_connection
from datetime import datetime


def extract_users() -> pd.DataFrame:
    """Extract users from PostgreSQL"""
    with Session(engine) as session:
        users = session.exec(select(User)).all()
        data = [
            {
                "user_id": u.id,
                "name": u.name,
                "email": u.email,
                "created_at": datetime.now().isoformat()
            }
            for u in users
        ]
    return pd.DataFrame(data)


def extract_seats() -> pd.DataFrame:
    """Extract seats from PostgreSQL"""
    with Session(engine) as session:
        seats = session.exec(select(Seat)).all()
        data = [
            {
                "seat_id": s.id,
                "instance_id": s.instance_id,
                "seat_number": s.seat_number,
                "class": s.class_,
                "status": s.status,
                "extracted_at": datetime.now().isoformat()
            }
            for s in seats
        ]
    return pd.DataFrame(data)


def extract_tickets() -> pd.DataFrame:
    """Extract tickets from PostgreSQL"""
    with Session(engine) as session:
        tickets = session.exec(select(Ticket)).all()
        data = [
            {
                "ticket_id": t.id,
                "user_id": t.user_id,
                "seat_id": t.seat_id,
                "status": t.status,
                "price": float(t.price),
                "extracted_at": datetime.now().isoformat()
            }
            for t in tickets
        ]
    return pd.DataFrame(data)


def extract_payments() -> pd.DataFrame:
    """Extract payments from PostgreSQL"""
    with Session(engine) as session:
        payments = session.exec(select(Payment)).all()
        data = [
            {
                "payment_id": p.id,
                "user_id": p.user_id,
                "total_price": float(p.total_price),
                "status": p.status,
                "purchased_date": p.purchased_date.isoformat() if p.purchased_date else datetime.now().isoformat(),
                "extracted_at": datetime.now().isoformat()
            }
            for p in payments
        ]
    return pd.DataFrame(data)


def load_to_snowflake_staging():
    """Load all data to Snowflake staging tables"""
    conn = get_snowflake_connection()
    cursor = conn.cursor()

    try:
        # Create staging schema if not exists
        cursor.execute("CREATE SCHEMA IF NOT EXISTS TICKET")
        print("✓ Staging schema ready")

        # Extract data
        print("\n📊 Extracting data from PostgreSQL...")
        users_df = extract_users()
        print(f"   ✓ Extracted {len(users_df)} users")

        seats_df = extract_seats()
        print(f"   ✓ Extracted {len(seats_df)} seats")

        tickets_df = extract_tickets()
        print(f"   ✓ Extracted {len(tickets_df)} tickets")

        payments_df = extract_payments()
        print(f"   ✓ Extracted {len(payments_df)} payments")

        # Load to Snowflake using SQL inserts
        print("\n📤 Loading to Snowflake...")
        
        # Users
        cursor.execute("DROP TABLE IF EXISTS TICKET.USERS")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS TICKET.USERS (
                USER_ID INTEGER,
                NAME VARCHAR(255),
                EMAIL VARCHAR(255),
                CREATED_AT VARCHAR(255)
            )
        """)
        for _, row in users_df.iterrows():
            user_id = int(row['user_id'])
            name = str(row['name']).replace("'", "''")
            email = str(row['email']).replace("'", "''")
            created_at = str(row['created_at'])
            cursor.execute(f"INSERT INTO TICKET.USERS VALUES ({user_id}, '{name}', '{email}', '{created_at}')")
        print(f"   ✓ Loaded {len(users_df)} users")
        
        # Seats
        cursor.execute("DROP TABLE IF EXISTS TICKET.SEATS")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS TICKET.SEATS (
                SEAT_ID INTEGER,
                INSTANCE_ID INTEGER,
                SEAT_NUMBER VARCHAR(10),
                CLASS VARCHAR(50),
                STATUS VARCHAR(50),
                EXTRACTED_AT VARCHAR(255)
            )
        """)
        for _, row in seats_df.iterrows():
            seat_id = int(row['seat_id'])
            instance_id = int(row['instance_id'])
            seat_number = str(row['seat_number']).replace("'", "''")
            class_val = str(row['class']).replace("'", "''")
            status = str(row['status']).replace("'", "''")
            extracted_at = str(row['extracted_at'])
            cursor.execute(f"INSERT INTO TICKET.SEATS VALUES ({seat_id}, {instance_id}, '{seat_number}', '{class_val}', '{status}', '{extracted_at}')")
        print(f"   ✓ Loaded {len(seats_df)} seats")
        
        # Tickets
        cursor.execute("DROP TABLE IF EXISTS TICKET.TICKETS")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS TICKET.TICKETS (
                TICKET_ID INTEGER,
                USER_ID INTEGER,
                SEAT_ID INTEGER,
                STATUS VARCHAR(50),
                PRICE DECIMAL(10, 2),
                EXTRACTED_AT VARCHAR(255)
            )
        """)
        for _, row in tickets_df.iterrows():
            ticket_id = int(row['ticket_id'])
            user_id = int(row['user_id'])
            seat_id = int(row['seat_id'])
            status = str(row['status']).replace("'", "''")
            price = float(row['price'])
            extracted_at = str(row['extracted_at'])
            cursor.execute(f"INSERT INTO TICKET.TICKETS VALUES ({ticket_id}, {user_id}, {seat_id}, '{status}', {price}, '{extracted_at}')")
        print(f"   ✓ Loaded {len(tickets_df)} tickets")
        
        # Payments
        cursor.execute("DROP TABLE IF EXISTS TICKET.PAYMENTS")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS TICKET.PAYMENTS (
                PAYMENT_ID INTEGER,
                USER_ID INTEGER,
                TOTAL_PRICE DECIMAL(10, 2),
                STATUS VARCHAR(50),
                PURCHASED_DATE VARCHAR(255),
                EXTRACTED_AT VARCHAR(255)
            )
        """)
        for _, row in payments_df.iterrows():
            payment_id = int(row['payment_id'])
            user_id = int(row['user_id'])
            total_price = float(row['total_price'])
            status = str(row['status']).replace("'", "''")
            purchased_date = str(row['purchased_date'])
            extracted_at = str(row['extracted_at'])
            cursor.execute(f"INSERT INTO TICKET.PAYMENTS VALUES ({payment_id}, {user_id}, {total_price}, '{status}', '{purchased_date}', '{extracted_at}')")
        print(f"   ✓ Loaded {len(payments_df)} payments")
        
        conn.commit()
        print("\n✅ Data staging complete!")

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()
