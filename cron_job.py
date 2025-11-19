"""Cron job script to run on a schedule."""
import sys
import os
from datetime import datetime
from db import db, init_db

def run_cron_job():
    """Main cron job function that runs every 24 hours.
    Adds an entry to the test_db table with a sequential number and timestamp.
    
    Returns:
        dict: A dictionary containing the execution results with keys:
            - success (bool): Whether the cron job completed successfully
            - timestamp (str): ISO format timestamp
            - sequence_number (int): The sequential number assigned to this entry
            - entry_id (int): The database ID of the created entry
            - total_entries (int): Total entries in test_db after insertion
            - errors (list): List of error messages if any
    """
    result = {
        'success': False,
        'timestamp': datetime.now().isoformat(),
        'sequence_number': 0,
        'entry_id': None,
        'total_entries': 0,
        'errors': []
    }
    
    try:
        print(f"[{result['timestamp']}] Cron job started")
        
        # Initialize database connection
        init_db()
        
        # Get the next sequential number (count existing entries + 1)
        try:
            count_query = "SELECT COUNT(*) as total FROM test_db;"
            count_result = db.execute_query(count_query)
            if count_result and len(count_result) > 0:
                result['sequence_number'] = count_result[0]['total'] + 1
            else:
                result['sequence_number'] = 1
        except Exception as e:
            error_msg = f"Error getting sequence number: {str(e)}"
            result['errors'].append(error_msg)
            print(f"[{datetime.now().isoformat()}] {error_msg}")
            result['sequence_number'] = 1  # Default to 1 if count fails
        
        # Insert new entry with sequential number and current timestamp
        try:
            run_timestamp = datetime.now()
            insert_query = """
            INSERT INTO test_db (sequence_number, run_timestamp) 
            VALUES (%s, %s) 
            RETURNING id, sequence_number, run_timestamp;
            """
            insert_result = db.execute_query(insert_query, (result['sequence_number'], run_timestamp))
            
            if insert_result:
                result['entry_id'] = insert_result['id']
                result['sequence_number'] = insert_result['sequence_number']
                print(f"[{datetime.now().isoformat()}] Added entry #{result['sequence_number']} to test_db (ID: {result['entry_id']})")
            else:
                error_msg = "Failed to insert entry into test_db"
                result['errors'].append(error_msg)
                print(f"[{datetime.now().isoformat()}] {error_msg}")
        except Exception as e:
            error_msg = f"Error inserting entry: {str(e)}"
            result['errors'].append(error_msg)
            print(f"[{datetime.now().isoformat()}] {error_msg}")
        
        # Get total entries count after insertion
        try:
            stats_query = "SELECT COUNT(*) as total FROM test_db;"
            stats_result = db.execute_query(stats_query)
            if stats_result and len(stats_result) > 0:
                result['total_entries'] = stats_result[0]['total']
                print(f"[{datetime.now().isoformat()}] Total entries in test_db: {result['total_entries']}")
        except Exception as e:
            error_msg = f"Error getting statistics: {str(e)}"
            result['errors'].append(error_msg)
            print(f"[{datetime.now().isoformat()}] {error_msg}")
        
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

