"""Analytics reports - Generate business intelligence reports"""
from src.snowflake import execute_query_dict


def print_section(title: str):
    """Print formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def report_revenue_summary():
    """Revenue summary report"""
    print_section("💰 REVENUE SUMMARY")

    results = execute_query_dict("""
        SELECT * FROM TICKET_ANALYTICS.VW_REVENUE_SUMMARY LIMIT 10
    """)

    if results:
        total_revenue = 0
        total_payments = 0

        for row in results:
            date_str = str(row['REVENUE_DATE'])
            payment_count = row['PAYMENT_COUNT']
            total_price = row['TOTAL_PRICE']
            avg_payment = row['AVG_PAYMENT']
            customers = row['UNIQUE_CUSTOMERS']

            total_revenue += float(total_price) if total_price else 0
            total_payments += payment_count

            print(f"📅 {date_str}")
            print(f"   💵 Revenue: ${total_price:,.2f}")
            print(f"   📊 Payments: {payment_count}")
            print(f"   👥 Customers: {customers}")
            print(f"   📈 Avg Payment: ${avg_payment:,.2f}")

        print(f"\n📊 SUMMARY:")
        print(f"   Total Revenue: ${total_revenue:,.2f}")
        print(f"   Total Payments: {total_payments}")
    else:
        print("❌ No revenue data yet")


def report_occupancy_metrics():
    """Seat occupancy report"""
    print_section("✈️ OCCUPANCY METRICS")

    results = execute_query_dict("""
        SELECT * FROM TICKET_ANALYTICS.VW_OCCUPANCY_BY_CLASS
    """)

    if results:
        for row in results:
            seat_class = row['SEAT_CLASS']
            total = row['TOTAL_SEATS']
            occupied = row['OCCUPIED_SEATS']
            available = row['AVAILABLE_SEATS']
            occupancy = row['OCCUPANCY_RATE_PCT']

            bar_length = int(occupancy / 5)
            bar = "█" * bar_length + "░" * (20 - bar_length)

            print(f"\n🪑 {seat_class.upper()}")
            print(f"   Occupancy: {bar} {occupancy:.1f}%")
            print(f"   Occupied: {occupied}/{total} seats")
            print(f"   Available: {available} seats")
    else:
        print("❌ No occupancy data yet")


def report_customer_metrics():
    """Customer analysis report"""
    print_section("👥 CUSTOMER METRICS")

    results = execute_query_dict("""
        SELECT * FROM TICKET_ANALYTICS.VW_CUSTOMER_METRICS LIMIT 10
    """)

    if results:
        segments = {}
        total_ltv = 0

        for row in results:
            name = row['NAME']
            bookings = row['TOTAL_BOOKINGS']
            ltv = row['LIFETIME_VALUE']
            segment = row['CUSTOMER_SEGMENT']

            if segment not in segments:
                segments[segment] = {"count": 0, "revenue": 0}
            segments[segment]["count"] += 1
            segments[segment]["revenue"] += float(ltv) if ltv else 0
            total_ltv += float(ltv) if ltv else 0

            print(f"\n👤 {name}")
            print(f"   Bookings: {bookings}")
            print(f"   Lifetime Value: ${ltv:,.2f}")
            print(f"   Segment: {segment}")

        print(f"\n📊 CUSTOMER SEGMENTS:")
        for segment, data in sorted(segments.items()):
            print(
                f"   {segment}: {data['count']} customers, ${data['revenue']:,.2f} revenue")

        print(f"\n💰 Total Customer Lifetime Value: ${total_ltv:,.2f}")
    else:
        print("❌ No customer data yet")


def report_booking_funnel():
    """Booking funnel analysis"""
    print_section("🔀 BOOKING FUNNEL")

    results = execute_query_dict("""
        SELECT * FROM TICKET_ANALYTICS.VW_BOOKING_FUNNEL ORDER BY PCT DESC
    """)

    if results:
        for row in results:
            stage = row['STAGE']
            count = row['COUNT_VAL']
            pct = row['PCT']

            bar_length = int(pct / 5)
            bar = "▓" * bar_length + "░" * (20 - bar_length)

            print(f"\n{stage}")
            print(f"   {bar} {pct:.1f}%")
            print(f"   Count: {count}")
    else:
        print("❌ No funnel data yet")


def report_all():
    """Generate all analytics reports"""
    print("\n" + "="*60)
    print("ANALYTICS REPORTS")
    print("="*60)

    report_revenue_summary()
    report_occupancy_metrics()
    report_customer_metrics()
    report_booking_funnel()

    print("\n" + "="*60)
    print("END OF REPORTS")
    print("="*60 + "\n")


def get_kpi_summary():
    """Get key performance indicators"""
    print_section("📊 KEY PERFORMANCE INDICATORS")

    # Total Revenue
    result = execute_query_dict("""
        SELECT SUM(TOTAL_PRICE) as TOTAL_REVENUE 
        FROM TICKET_ANALYTICS.FACT_PAYMENTS 
        WHERE PAYMENT_STATUS = 'completed'
    """)
    total_rev = float(result[0]['TOTAL_REVENUE']
                      ) if result and result[0]['TOTAL_REVENUE'] else 0
    print(f"💵 Total Revenue: ${total_rev:,.2f}")

    # Total Bookings
    result = execute_query_dict(
        "SELECT COUNT(*) as COUNT FROM TICKET_ANALYTICS.FACT_BOOKINGS")
    total_bookings = result[0]['COUNT'] if result else 0
    print(f"📋 Total Bookings: {total_bookings}")

    # Confirmed Bookings
    result = execute_query_dict("""
        SELECT COUNT(*) as COUNT 
        FROM TICKET_ANALYTICS.FACT_BOOKINGS 
        WHERE TICKET_STATUS = 'confirmed'
    """)
    confirmed = result[0]['COUNT'] if result else 0
    print(f"✅ Confirmed Bookings: {confirmed}")

    # Conversion Rate
    conversion = (confirmed / total_bookings *
                  100) if total_bookings > 0 else 0
    print(f"📈 Conversion Rate: {conversion:.1f}%")

    # Total Customers
    result = execute_query_dict(
        "SELECT COUNT(*) as COUNT FROM TICKET_ANALYTICS.DIM_USERS")
    total_customers = result[0]['COUNT'] if result else 0
    print(f"👥 Total Customers: {total_customers}")

    # Average Occupancy
    result = execute_query_dict("""
        SELECT AVG(OCCUPANCY_RATE_PCT) as AVG_OCC 
        FROM TICKET_ANALYTICS.FACT_SEAT_SNAPSHOT
    """)
    avg_occ = float(result[0]['AVG_OCC']
                    ) if result and result[0]['AVG_OCC'] else 0
    print(f"✈️ Average Occupancy: {avg_occ:.1f}%")
