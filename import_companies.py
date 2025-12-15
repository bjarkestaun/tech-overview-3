"""Script to import companies data from CSV into the database."""
import csv
from datetime import datetime
from db import db, init_db

def create_companies_table():
    """Create the companies table if it doesn't exist."""
    create_table_query = """
    CREATE TABLE IF NOT EXISTS companies (
        id SERIAL PRIMARY KEY,
        organization_name VARCHAR(500),
        organization_name_url TEXT,
        last_funding_date DATE,
        last_funding_type VARCHAR(255),
        last_funding_amount NUMERIC,
        last_funding_amount_currency VARCHAR(10),
        last_funding_amount_usd NUMERIC,
        industries TEXT,
        headquarters_location VARCHAR(500),
        description TEXT,
        cb_rank_company INTEGER,
        founded_date DATE,
        founded_date_precision VARCHAR(50),
        company_type VARCHAR(100),
        website TEXT,
        full_description TEXT,
        number_of_employees VARCHAR(100),
        total_funding_amount NUMERIC,
        total_funding_amount_currency VARCHAR(10),
        total_funding_amount_usd NUMERIC,
        top_5_investors TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    try:
        db.execute_query(create_table_query)
        print("Companies table created successfully")
    except Exception as error:
        print(f"Error creating companies table: {error}")
        raise

def parse_date(date_str, precision):
    """Parse date string based on precision."""
    if not date_str or date_str.strip() == '':
        return None
    
    try:
        date_str = date_str.strip()
        if precision == 'day':
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        elif precision == 'month':
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        elif precision == 'year':
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            # Try to parse as YYYY-MM-DD
            return datetime.strptime(date_str, '%Y-%m-%d').date()
    except Exception:
        return None

def parse_number(value):
    """Parse numeric value, handling empty strings."""
    if not value or value.strip() == '':
        return None
    try:
        return float(value.replace(',', ''))
    except Exception:
        return None

def parse_integer(value):
    """Parse integer value, handling empty strings."""
    if not value or value.strip() == '':
        return None
    try:
        return int(value)
    except Exception:
        return None

def import_companies_from_csv(csv_file_path):
    """Import companies data from CSV file."""
    # Initialize database and create table
    init_db()
    create_companies_table()
    
    # Clear existing data (optional - comment out if you want to keep existing data)
    try:
        db.execute_query("TRUNCATE TABLE companies RESTART IDENTITY CASCADE;", fetch=False)
        print("Cleared existing companies data")
    except Exception as e:
        print(f"Note: Could not clear existing data: {e}")
    
    inserted_count = 0
    error_count = 0
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                try:
                    # Parse dates
                    last_funding_date = parse_date(
                        row.get('Last Funding Date', ''),
                        row.get('Founded Date Precision', '')
                    )
                    founded_date = parse_date(
                        row.get('Founded Date', ''),
                        row.get('Founded Date Precision', '')
                    )
                    
                    # Prepare insert query
                    insert_query = """
                    INSERT INTO companies (
                        organization_name, organization_name_url, last_funding_date,
                        last_funding_type, last_funding_amount, last_funding_amount_currency,
                        last_funding_amount_usd, industries, headquarters_location,
                        description, cb_rank_company, founded_date, founded_date_precision,
                        company_type, website, full_description, number_of_employees,
                        total_funding_amount, total_funding_amount_currency,
                        total_funding_amount_usd, top_5_investors
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    );
                    """
                    
                    params = (
                        row.get('Organization Name', '') or None,
                        row.get('Organization Name URL', '') or None,
                        last_funding_date,
                        row.get('Last Funding Type', '') or None,
                        parse_number(row.get('Last Funding Amount', '')),
                        row.get('Last Funding Amount Currency', '') or None,
                        parse_number(row.get('Last Funding Amount (in USD)', '')),
                        row.get('Industries', '') or None,
                        row.get('Headquarters Location', '') or None,
                        row.get('Description', '') or None,
                        parse_integer(row.get('CB Rank (Company)', '')),
                        founded_date,
                        row.get('Founded Date Precision', '') or None,
                        row.get('Company Type', '') or None,
                        row.get('Website', '') or None,
                        row.get('Full Description', '') or None,
                        row.get('Number of Employees', '') or None,
                        parse_number(row.get('Total Funding Amount', '')),
                        row.get('Total Funding Amount Currency', '') or None,
                        parse_number(row.get('Total Funding Amount (in USD)', '')),
                        row.get('Top 5 Investors', '') or None
                    )
                    
                    db.execute_query(insert_query, params, fetch=False)
                    inserted_count += 1
                    
                    if inserted_count % 100 == 0:
                        print(f"Imported {inserted_count} companies...")
                        
                except Exception as e:
                    error_count += 1
                    print(f"Error importing row {inserted_count + error_count}: {e}")
                    continue
        
        print(f"\nImport completed!")
        print(f"Successfully imported: {inserted_count} companies")
        print(f"Errors: {error_count}")
        
    except FileNotFoundError:
        print(f"Error: CSV file not found: {csv_file_path}")
    except Exception as e:
        print(f"Error reading CSV file: {e}")

if __name__ == '__main__':
    csv_file_path = 'companies-30-08-2025.csv'
    import_companies_from_csv(csv_file_path)

