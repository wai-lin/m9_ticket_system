"""Task 4 Analytics Demo - Simple test without full business operations"""
import asyncio
from src.analytics import load_to_snowflake_staging, setup_analytics_schema, report_all


async def main():
    """Run Task 4 analytics demo"""
    print("\n" + "="*60)
    print("TASK 4: ANALYTICS & DATA WAREHOUSING")
    print("="*60)
    
    # Step 1: Load data
    print("\n📊 STEP 1: Extract and Load Data to Snowflake Staging")
    print("-"*60)
    try:
        load_to_snowflake_staging()
        print("✅ Data loaded successfully!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 2: Build analytics
    print("\n🏗️  STEP 2: Build Analytical Data Mart")
    print("-"*60)
    try:
        setup_analytics_schema()
        print("✅ Analytics schema created successfully!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 3: Generate reports
    print("\n📈 STEP 3: Generate Analytics Reports")
    print("-"*60)
    try:
        report_all()
        print("✅ Reports generated successfully!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return


if __name__ == "__main__":
    asyncio.run(main())
