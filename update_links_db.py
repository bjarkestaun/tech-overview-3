"""Script to update links table with external links from company websites."""
from datetime import date
from db import db, init_db
from functions import crawl_external_links, simplify_external_links

def update_links_from_companies(limit=10):
    """
    Get websites from companies database, crawl them, and save external links to links table.
    
    Args:
        limit: Number of companies to process (default: 10)
    
    Returns:
        dict: Summary of the operation with counts and any errors
    """
    result = {
        'companies_processed': 0,
        'links_inserted': 0,
        'errors': []
    }
    
    try:
        # Initialize database
        init_db()
        
        # Get first N companies with websites
        query = """
        SELECT id, organization_name, website 
        FROM companies 
        WHERE website IS NOT NULL AND website != ''
        ORDER BY cb_rank_company ASC NULLS LAST
        LIMIT %s;
        """
        
        companies = db.execute_query(query, (limit,))
        
        if not companies or len(companies) == 0:
            result['errors'].append("No companies with websites found")
            return result
        
        today = date.today()
        
        for company in companies:
            try:
                website = company['website']
                company_name = company['organization_name']
                
                if not website:
                    continue
                
                # Ensure website has a scheme (http:// or https://)
                if not website.startswith(('http://', 'https://')):
                    website = 'https://' + website
                
                # Crawl external links from the website
                external_links = crawl_external_links(website)
                
                # Simplify to get unique top-level domains
                simplified_domains = simplify_external_links(external_links)
                
                # Insert each simplified domain into links table
                for domain in simplified_domains:
                    try:
                        # Check if this combination already exists to avoid duplicates
                        check_query = """
                        SELECT id FROM links 
                        WHERE date = %s AND linking_url = %s AND url = %s
                        LIMIT 1;
                        """
                        existing = db.execute_query(check_query, (today, website, domain))
                        
                        if existing and len(existing) > 0:
                            # Already exists, skip
                            continue
                        
                        insert_query = """
                        INSERT INTO links (date, linking_url, url)
                        VALUES (%s, %s, %s);
                        """
                        db.execute_query(insert_query, (today, website, domain), fetch=False)
                        result['links_inserted'] += 1
                    except Exception as e:
                        error_msg = f"Error inserting link for {company_name}: {str(e)}"
                        result['errors'].append(error_msg)
                        continue
                
                result['companies_processed'] += 1
                
            except Exception as e:
                error_msg = f"Error processing {company.get('organization_name', 'unknown')}: {str(e)}"
                result['errors'].append(error_msg)
                continue
        
        return result
        
    except Exception as e:
        result['errors'].append(f"Fatal error: {str(e)}")
        return result

if __name__ == '__main__':
    print("Starting links update process...")
    result = update_links_from_companies(limit=10)
    
    print(f"\nProcess completed!")
    print(f"Companies processed: {result['companies_processed']}")
    print(f"Links inserted: {result['links_inserted']}")
    if result['errors']:
        print(f"\nErrors encountered: {len(result['errors'])}")
        for error in result['errors']:
            print(f"  - {error}")

