"""Cron job script to run on a schedule."""
import sys
import os
from datetime import datetime
from db import db, init_db

def run_cron_job():
    """Main cron job function that runs every 24 hours.
    
    Returns:
        dict: A dictionary containing the execution results with keys:
            - success (bool): Whether the cron job completed successfully
            - timestamp (str): ISO format timestamp
            - deleted_count (int): Number of entries deleted
            - total_entries (int): Total entries after cleanup
            - errors (list): List of error messages if any
    """
    result = {
        'success': False,
        'timestamp': datetime.now().isoformat(),
        'deleted_count': 0,
        'total_entries': 0,
        'errors': []
    }
    
    try:
        print(f"[{result['timestamp']}] Cron job started")
        
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
            result['deleted_count'] = deleted_count if deleted_count else 0
            print(f"[{datetime.now().isoformat()}] Cleaned up {result['deleted_count']} old entries")
        except Exception as e:
            error_msg = f"Error during cleanup: {str(e)}"
            result['errors'].append(error_msg)
            print(f"[{datetime.now().isoformat()}] {error_msg}")
        
        # Example: Get statistics
        try:
            stats_query = "SELECT COUNT(*) as total FROM entries;"
            stats_result = db.execute_query(stats_query)
            if stats_result and len(stats_result) > 0:
                result['total_entries'] = stats_result[0]['total']
                print(f"[{datetime.now().isoformat()}] Total entries in database: {result['total_entries']}")
        except Exception as e:
            error_msg = f"Error getting statistics: {str(e)}"
            result['errors'].append(error_msg)
            print(f"[{datetime.now().isoformat()}] {error_msg}")
        
        # Add your custom cron job logic here
        # Examples:
        # - Data aggregation
        # - Sending reports
        # - Database maintenance
        # - API data synchronization
        
        result['success'] = len(result['errors']) == 0
        print(f"[{datetime.now().isoformat()}] Cron job completed {'successfully' if result['success'] else 'with errors'}")
        return result
        
    except Exception as e:
        error_msg = f"Cron job failed: {str(e)}"
        result['errors'].append(error_msg)
        result['success'] = False
        print(f"[{datetime.now().isoformat()}] {error_msg}")
        return result

if __name__ == '__main__':
    result = run_cron_job()
    sys.exit(0 if result['success'] else 1)

