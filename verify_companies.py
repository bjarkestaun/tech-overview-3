"""Script to verify companies data in the database."""
from db import db

def verify_companies():
    """Verify that companies data exists in the database."""
    try:
        # Count total companies
        count_query = "SELECT COUNT(*) as total FROM companies;"
        count_result = db.execute_query(count_query)
        
        if count_result and len(count_result) > 0:
            total = count_result[0]['total']
            print(f"Total companies in database: {total}")
        else:
            print("No companies found in database")
            return
        
        # Get a sample of companies
        sample_query = """
        SELECT 
            id, 
            organization_name, 
            website, 
            headquarters_location,
            cb_rank_company,
            founded_date
        FROM companies 
        ORDER BY cb_rank_company ASC NULLS LAST
        LIMIT 10;
        """
        
        sample_result = db.execute_query(sample_query)
        
        if sample_result and len(sample_result) > 0:
            print("\nSample companies (top 10 by rank):")
            print("-" * 100)
            for company in sample_result:
                print(f"ID: {company['id']}")
                print(f"  Name: {company['organization_name']}")
                print(f"  Website: {company['website']}")
                print(f"  Location: {company['headquarters_location']}")
                print(f"  Rank: {company['cb_rank_company']}")
                print(f"  Founded: {company['founded_date']}")
                print("-" * 100)
        else:
            print("No sample data found")
        
        # Check for companies with websites
        website_query = "SELECT COUNT(*) as total FROM companies WHERE website IS NOT NULL AND website != '';"
        website_result = db.execute_query(website_query)
        if website_result and len(website_result) > 0:
            print(f"\nCompanies with websites: {website_result[0]['total']}")
        
        # Check date ranges
        date_query = """
        SELECT 
            MIN(founded_date) as earliest,
            MAX(founded_date) as latest
        FROM companies 
        WHERE founded_date IS NOT NULL;
        """
        date_result = db.execute_query(date_query)
        if date_result and len(date_result) > 0 and date_result[0]['earliest']:
            print(f"\nDate range:")
            print(f"  Earliest founded: {date_result[0]['earliest']}")
            print(f"  Latest founded: {date_result[0]['latest']}")
        
    except Exception as e:
        print(f"Error verifying companies: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    verify_companies()

