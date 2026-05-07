from extract import extract_all_files
from sales_ETL.extract import extract_from_csv
from transform import transform_data
from load import *
from config import get_timestamp
from datetime import datetime
import pandas as pd


def run_etl_pipeline():
    """Run the complete ETL pipeline"""
    try:
        print(f"\n🚀 === Starting ETL Pipeline - {datetime.now()} ===\n")

        # Step 1: Extract
        extracted_data = extract_all_files()

        if not extracted_data:
            print("No data to process. Exiting...")
            return

        # Step 2 & 3: Process each file
        for file_name, raw_df in extracted_data:
            print(f"\n📂 Processing file: {file_name}")

            # Transform
            clean_df = transform_data(raw_df)

            # Load
            # load_to_postgres(clean_df)
            load_to_snowflake(clean_df)
            # Generate Report
            report_path = f"reports/sales_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            clean_df.to_csv(report_path, index=False)
            print(f"📊 Report saved: {report_path}")

        print(f"\n🎉 === ETL Pipeline Completed Successfully! ===\n")

    except Exception as e:
        print(f"[{get_timestamp()}] ❌ Critical Error in ETL Pipeline: {e}")


# ====================== SCHEDULER ======================
from apscheduler.schedulers.blocking import BlockingScheduler
import logging


def start_scheduler():
    """Start automated daily ETL scheduler"""
    scheduler = BlockingScheduler()

    # Run every day at 8:00 AM
    scheduler.add_job(run_etl_pipeline, 'cron', hour=8, minute=0)

    # Also run every 2 hours for testing
    scheduler.add_job(run_etl_pipeline, 'interval', minutes=1)

    print(f"[{get_timestamp()}] ⏰ Scheduler started. ETL will run automatically.")
    print("Press Ctrl+C to stop the scheduler.")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\n⛔ Scheduler stopped.")


if __name__ == "__main__":
    # Choose how you want to run:

    # Option 1: Run once (for testing)
    run_etl_pipeline()

    # Option 2: Start Scheduler (Uncomment below lines)
    start_scheduler()