"""Database connection and utility functions."""
import psycopg2
from psycopg2 import pool, sql
from psycopg2.extras import RealDictCursor
import os
from config import Config


class Database:
    """Database connection manager."""
    
    def __init__(self):
        self.connection_pool = None
        self._create_connection_pool()
    
    def _create_connection_pool(self):
        """Create a connection pool for database connections."""
        try:
            self.connection_pool = psycopg2.pool.SimpleConnectionPool(
                1, 20,
                dsn=Config.DATABASE_URL,
                cursor_factory=RealDictCursor
            )
            if self.connection_pool:
                print("Connection pool created successfully")
        except (Exception, psycopg2.Error) as error:
            print(f"Error while connecting to PostgreSQL: {error}")
            self.connection_pool = None
    
    def get_connection(self):
        """Get a connection from the pool."""
        if self.connection_pool:
            return self.connection_pool.getconn()
        return None
    
    def return_connection(self, connection):
        """Return a connection to the pool."""
        if self.connection_pool:
            self.connection_pool.putconn(connection)
    
    def execute_query(self, query, params=None, fetch=True):
        """Execute a query and return results."""
        connection = self.get_connection()
        if connection is None:
            return None
        
        try:
            cursor = connection.cursor()
            cursor.execute(query, params)
            
            # Check if it's a query that returns data
            if cursor.description and fetch:
                # Check if query has RETURNING clause (INSERT/UPDATE with RETURNING)
                # Convert query to string for checking
                query_upper = str(query).upper() if query else ''
                if 'RETURNING' in query_upper:
                    # INSERT/UPDATE with RETURNING - fetch single row
                    results = cursor.fetchone()
                    connection.commit()
                    cursor.close()
                    self.return_connection(connection)
                    return results
                else:
                    # Regular SELECT query - fetch all rows
                    results = cursor.fetchall()
                    cursor.close()
                    self.return_connection(connection)
                    return results
            else:
                # INSERT/UPDATE/DELETE without RETURNING
                connection.commit()
                affected_rows = cursor.rowcount
                cursor.close()
                self.return_connection(connection)
                return affected_rows
        except (Exception, psycopg2.Error) as error:
            print(f"Error executing query: {error}")
            connection.rollback()
            cursor.close()
            self.return_connection(connection)
            raise error
    
    def close_all_connections(self):
        """Close all connections in the pool."""
        if self.connection_pool:
            self.connection_pool.closeall()
            print("All database connections closed")


# Global database instance
db = Database()


def init_db():
    """Initialize database tables if they don't exist."""
    # Example: Create a simple table for testing
    create_table_query = """
    CREATE TABLE IF NOT EXISTS entries (
        id SERIAL PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        content TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    try:
        db.execute_query(create_table_query)
        print("Database tables initialized successfully")
    except Exception as error:
        print(f"Error initializing database: {error}")

