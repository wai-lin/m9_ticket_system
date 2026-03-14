"""Analytics data model - Create fact and dimension tables in Snowflake"""
from src.snowflake import get_snowflake_connection


def clear_all_data():
    conn = get_snowflake_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DROP SCHEMA IF EXISTS STAGING CASCADE")
        print("✓ Dropped existing STAGING schema")
        cursor.execute("DROP SCHEMA IF EXISTS TICET_ANALYTICS CASCADE")
        print("✓ Dropped existing TICET_ANALYTICS schema")
        cursor.execute("DROP SCHEMA IF EXISTS TICKET CASCADE")
        print("✓ Dropped existing TICKET schema")
    finally:
        cursor.close()
        conn.close()


def create_analytics_schema():
    """Create analytics schema"""
    conn = get_snowflake_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("CREATE SCHEMA IF NOT EXISTS TICKET_ANALYTICS")
        print("✓ Created TICKET_ANALYTICS schema")
    finally:
        cursor.close()
        conn.close()


def create_fact_tables():
    """Create fact tables from staging data"""
    conn = get_snowflake_connection()
    cursor = conn.cursor()

    try:
        # Create FACT_BOOKINGS - one row per ticket
        print("📋 Creating FACT_BOOKINGS...")
        cursor.execute("""
            CREATE OR REPLACE TABLE TICKET_ANALYTICS.FACT_BOOKINGS AS
            SELECT
                t.TICKET_ID,
                t.USER_ID,
                t.SEAT_ID,
                s.INSTANCE_ID,
                s.CLASS as SEAT_CLASS,
                t.STATUS as TICKET_STATUS,
                t.PRICE as TICKET_PRICE,
                CURRENT_TIMESTAMP as BOOKING_DATE,
                CURRENT_TIMESTAMP as LOAD_DATE
            FROM TICKET.TICKETS t
            LEFT JOIN TICKET.SEATS s ON t.SEAT_ID = s.SEAT_ID
        """)
        cursor.execute("SELECT COUNT(*) FROM TICKET_ANALYTICS.FACT_BOOKINGS")
        count = cursor.fetchone()[0]
        print(f"   ✓ Created FACT_BOOKINGS with {count} rows")

        # Create FACT_PAYMENTS - one row per payment
        print("📋 Creating FACT_PAYMENTS...")
        cursor.execute("""
            CREATE OR REPLACE TABLE TICKET_ANALYTICS.FACT_PAYMENTS AS
            SELECT
                p.PAYMENT_ID,
                p.USER_ID,
                p.TOTAL_PRICE,
                p.STATUS as PAYMENT_STATUS,
                p.PURCHASED_DATE,
                CURRENT_TIMESTAMP as LOAD_DATE
            FROM TICKET.PAYMENTS p
        """)
        cursor.execute("SELECT COUNT(*) FROM TICKET_ANALYTICS.FACT_PAYMENTS")
        count = cursor.fetchone()[0]
        print(f"   ✓ Created FACT_PAYMENTS with {count} rows")

        # Create FACT_SEAT_SNAPSHOT - seat availability snapshot
        print("📋 Creating FACT_SEAT_SNAPSHOT...")
        cursor.execute("""
            CREATE OR REPLACE TABLE TICKET_ANALYTICS.FACT_SEAT_SNAPSHOT AS
            SELECT
                s.INSTANCE_ID,
                s.CLASS,
                COUNT(*) as TOTAL_SEATS,
                SUM(CASE WHEN s.STATUS = 'available' THEN 1 ELSE 0 END) as AVAILABLE_SEATS,
                SUM(CASE WHEN s.STATUS = 'occupied' THEN 1 ELSE 0 END) as OCCUPIED_SEATS,
                ROUND(
                    SUM(CASE WHEN s.STATUS = 'occupied' THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
                    2
                ) as OCCUPANCY_RATE_PCT,
                CURRENT_TIMESTAMP as SNAPSHOT_DATE
            FROM TICKET.SEATS s
            GROUP BY s.INSTANCE_ID, s.CLASS
        """)
        cursor.execute(
            "SELECT COUNT(*) FROM TICKET_ANALYTICS.FACT_SEAT_SNAPSHOT")
        count = cursor.fetchone()[0]
        print(f"   ✓ Created FACT_SEAT_SNAPSHOT with {count} rows")

        conn.commit()

    finally:
        cursor.close()
        conn.close()


def create_dimension_tables():
    """Create dimension tables"""
    conn = get_snowflake_connection()
    cursor = conn.cursor()

    try:
        # Create DIM_USERS
        print("📊 Creating DIM_USERS...")
        cursor.execute("""
            CREATE OR REPLACE TABLE TICKET_ANALYTICS.DIM_USERS AS
            SELECT
                u.USER_ID,
                u.NAME,
                u.EMAIL,
                u.CREATED_AT as REGISTRATION_DATE,
                COUNT(DISTINCT t.TICKET_ID) as TOTAL_BOOKINGS,
                COALESCE(SUM(t.PRICE), 0) as LIFETIME_VALUE,
                CURRENT_TIMESTAMP as LOAD_DATE
            FROM TICKET.USERS u
            LEFT JOIN TICKET.TICKETS t ON u.USER_ID = t.USER_ID 
                AND t.STATUS IN ('confirmed', 'pending')
            GROUP BY u.USER_ID, u.NAME, u.EMAIL, u.CREATED_AT
        """)
        cursor.execute("SELECT COUNT(*) FROM TICKET_ANALYTICS.DIM_USERS")
        count = cursor.fetchone()[0]
        print(f"   ✓ Created DIM_USERS with {count} rows")

        # Create DIM_SEAT_CLASSES
        print("📊 Creating DIM_SEAT_CLASSES...")
        cursor.execute("""
            CREATE OR REPLACE TABLE TICKET_ANALYTICS.DIM_SEAT_CLASSES AS
            SELECT DISTINCT
                CLASS as CLASS_NAME,
                CASE
                    WHEN CLASS = 'economy' THEN 1.0
                    WHEN CLASS = 'business' THEN 3.0
                    WHEN CLASS = 'first' THEN 5.0
                    ELSE 1.5
                END as PRICE_MULTIPLIER,
                CURRENT_TIMESTAMP as LOAD_DATE
            FROM TICKET.SEATS
        """)
        cursor.execute("SELECT COUNT(*) FROM TICKET_ANALYTICS.DIM_SEAT_CLASSES")
        count = cursor.fetchone()[0]
        print(f"   ✓ Created DIM_SEAT_CLASSES with {count} rows")

        conn.commit()

    finally:
        cursor.close()
        conn.close()


def create_analytical_views():
    """Create analytical views for reporting"""
    conn = get_snowflake_connection()
    cursor = conn.cursor()

    try:
        # Revenue Summary
        print("📈 Creating analytical views...")
        cursor.execute("""
            CREATE OR REPLACE VIEW TICKET_ANALYTICS.VW_REVENUE_SUMMARY AS
            SELECT
                DATE_TRUNC('day', TRY_TO_TIMESTAMP(p.PURCHASED_DATE)) as REVENUE_DATE,
                COUNT(DISTINCT p.PAYMENT_ID) as PAYMENT_COUNT,
                SUM(p.TOTAL_PRICE) as TOTAL_REVENUE,
                AVG(p.TOTAL_PRICE) as AVG_PAYMENT,
                COUNT(DISTINCT p.USER_ID) as UNIQUE_CUSTOMERS
            FROM TICKET_ANALYTICS.FACT_PAYMENTS p
            WHERE p.PAYMENT_STATUS = 'completed'
            GROUP BY DATE_TRUNC('day', TRY_TO_TIMESTAMP(p.PURCHASED_DATE))
            ORDER BY REVENUE_DATE DESC
        """)
        print("   ✓ VW_REVENUE_SUMMARY")

        # Occupancy Trends
        cursor.execute("""
            CREATE OR REPLACE VIEW TICKET_ANALYTICS.VW_OCCUPANCY_BY_CLASS AS
            SELECT
                CLASS as SEAT_CLASS,
                TOTAL_SEATS,
                OCCUPIED_SEATS,
                AVAILABLE_SEATS,
                OCCUPANCY_RATE_PCT
            FROM TICKET_ANALYTICS.FACT_SEAT_SNAPSHOT
            ORDER BY OCCUPANCY_RATE_PCT DESC
        """)
        print("   ✓ VW_OCCUPANCY_BY_CLASS")

        # Customer Metrics
        cursor.execute("""
            CREATE OR REPLACE VIEW TICKET_ANALYTICS.VW_CUSTOMER_METRICS AS
            SELECT
                USER_ID,
                NAME,
                EMAIL,
                REGISTRATION_DATE,
                TOTAL_BOOKINGS,
                LIFETIME_VALUE,
                CASE
                    WHEN TOTAL_BOOKINGS >= 5 THEN 'VIP'
                    WHEN TOTAL_BOOKINGS >= 2 THEN 'Regular'
                    ELSE 'Occasional'
                END as CUSTOMER_SEGMENT
            FROM TICKET_ANALYTICS.DIM_USERS
            WHERE TOTAL_BOOKINGS > 0
            ORDER BY LIFETIME_VALUE DESC
        """)
        print("   ✓ VW_CUSTOMER_METRICS")

        # Booking Funnel
        cursor.execute("""
            CREATE OR REPLACE VIEW TICKET_ANALYTICS.VW_BOOKING_FUNNEL AS
            SELECT
                'Total Bookings' as STAGE,
                COUNT(*) as COUNT_VAL,
                100.0 as PCT
            FROM TICKET_ANALYTICS.FACT_BOOKINGS
            UNION ALL
            SELECT
                'Confirmed',
                COUNT(*),
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM TICKET_ANALYTICS.FACT_BOOKINGS), 2)
            FROM TICKET_ANALYTICS.FACT_BOOKINGS
            WHERE TICKET_STATUS = 'confirmed'
            UNION ALL
            SELECT
                'Paid',
                COUNT(*),
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM TICKET_ANALYTICS.FACT_BOOKINGS), 2)
            FROM TICKET_ANALYTICS.FACT_PAYMENTS
            WHERE PAYMENT_STATUS = 'completed'
        """)
        print("   ✓ VW_BOOKING_FUNNEL")

        conn.commit()
        print("\n✅ Analytical views created!")

    finally:
        cursor.close()
        conn.close()


def setup_analytics_schema():
    """Full setup: schema + fact + dimension tables + views"""
    print("\n" + "="*60)
    print("ANALYTICS DATA MART SETUP")
    print("="*60)

    create_analytics_schema()
    create_fact_tables()
    create_dimension_tables()
    create_analytical_views()

    print("\n" + "="*60)
