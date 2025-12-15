"""Script to create the links table in the database."""
from db import db, init_db

def create_links_table():
    """Create the links table if it doesn't exist."""
    create_table_query = """
    CREATE TABLE IF NOT EXISTS links (
        id SERIAL PRIMARY KEY,
        date DATE NOT NULL,
        linking_url TEXT NOT NULL,
        url TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    try:
        db.execute_query(create_table_query)
        print("Links table created successfully")
        
        # Verify table exists
        verify_query = """
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'links'
        ORDER BY ordinal_position;
        """
        result = db.execute_query(verify_query)
        
        if result:
            print("\nTable structure:")
            for row in result:
                print(f"  - {row['column_name']}: {row['data_type']}")
        else:
            print("Warning: Could not verify table structure")
            
    except Exception as error:
        print(f"Error creating links table: {error}")
        raise

if __name__ == '__main__':
    init_db()
    create_links_table()

