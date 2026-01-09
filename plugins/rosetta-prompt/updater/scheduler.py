"""
Weekly scheduler for the Prompting Guide Updater Agent.

This script can be run as a background process or set up as a cron job.
It triggers the updater agent once per week.
"""
import asyncio
import schedule
import time
from datetime import datetime

from agent import run_updater


def scheduled_update():
    """Run the update as a scheduled job."""
    print(f"\n{'=' * 60}")
    print(f"SCHEDULED UPDATE - {datetime.utcnow().isoformat()}")
    print(f"{'=' * 60}")
    
    try:
        asyncio.run(run_updater())
    except Exception as e:
        print(f"Error during scheduled update: {e}")


def run_scheduler():
    """Start the weekly scheduler."""
    print("Prompting Guide Updater Scheduler Started")
    print("Updates will run every Sunday at 00:00 UTC")
    print("-" * 60)
    
    # Schedule weekly run on Sundays at midnight UTC
    schedule.every().sunday.at("00:00").do(scheduled_update)
    
    # Also run immediately on start for testing
    print("Running initial update...")
    scheduled_update()
    
    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(3600)  # Check every hour


if __name__ == "__main__":
    run_scheduler()

