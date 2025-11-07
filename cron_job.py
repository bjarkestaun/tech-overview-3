"""Cron job script to run on a schedule."""
import sys
import os
from datetime import datetime
from db import db, init_db

def run_cron_job():
    """Main cron job function that runs every 24 hours."""
    try:
        print(f"[{datetime.now().isoformat()}] Cron job started")
        
        # Initialize database connection
        init_db()
        
        # Example: Clean up old entries (older than 30 days)
        # You can customize this based on your needs
        cleanup_query = """
        DELETE FROM entries 
        WHERE created_at < NOW() - INTERVAL '30 days';
        """
        
        try:
            deleted_count = db.execute_query(cleanup_query, fetch=False)
            print(f"[{datetime.now().isoformat()}] Cleaned up {deleted_count} old entries")
        except Exception as e:
            print(f"[{datetime.now().isoformat()}] Error during cleanup: {e}")
        
        # Example: Get statistics
        try:
            stats_query = "SELECT COUNT(*) as total FROM entries;"
            result = db.execute_query(stats_query)
            if result and len(result) > 0:
                total_entries = result[0]['total']
                print(f"[{datetime.now().isoformat()}] Total entries in database: {total_entries}")
        except Exception as e:
            print(f"[{datetime.now().isoformat()}] Error getting statistics: {e}")
        
        # Add your custom cron job logic here
        # Examples:
        # - Data aggregation
        # - Sending reports
        # - Database maintenance
        # - API data synchronization
        
        print(f"[{datetime.now().isoformat()}] Cron job completed successfully")
        return 0
        
    except Exception as e:
        print(f"[{datetime.now().isoformat()}] Cron job failed: {e}")
        return 1

if __name__ == '__main__':
    exit_code = run_cron_job()
    sys.exit(exit_code)

