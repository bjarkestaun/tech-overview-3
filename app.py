from datetime import datetime
from flask import Flask, jsonify, request, render_template_string
from config import Config
from db import db, init_db
from cron_job import run_cron_job

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database on startup
init_db()

@app.route('/')
def home():
    """Home endpoint"""
    return jsonify({
        'message': 'Welcome to Tech Overview 3 API',
        'status': 'running',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/health')
def health():
    """Health check endpoint (required for Render)"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/api/status')
def status():
    """API status endpoint"""
    return jsonify({
        'environment': app.config['ENV'],
        'port': app.config['PORT'],
        'message': 'API is running'
    })

@app.route('/api/db/test', methods=['GET'])
def test_db():
    """Test database connection"""
    try:
        result = db.execute_query("SELECT version();")
        if result:
            return jsonify({
                'status': 'connected',
                'database_version': result[0]['version'],
                'timestamp': datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to connect to database'
            }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/entries', methods=['GET'])
def get_entries():
    """Get all entries from the database"""
    try:
        query = "SELECT * FROM entries ORDER BY created_at DESC LIMIT 100;"
        results = db.execute_query(query)
        if results is not None:
            # Convert RealDictRow to dict for JSON serialization
            entries = [dict(row) for row in results]
            return jsonify({
                'entries': entries,
                'count': len(entries)
            }), 200
        else:
            return jsonify({
                'entries': [],
                'count': 0
            }), 200
    except Exception as e:
        return jsonify({
            'error': 'Database error',
            'message': str(e)
        }), 500

@app.route('/api/entries', methods=['POST'])
def create_entry():
    """Create a new entry"""
    try:
        data = request.get_json()
        if not data or 'title' not in data:
            return jsonify({
                'error': 'Bad request',
                'message': 'Title is required'
            }), 400
        
        title = data.get('title')
        content = data.get('content', '')
        
        query = "INSERT INTO entries (title, content) VALUES (%s, %s) RETURNING id, title, content, created_at;"
        result = db.execute_query(query, (title, content))
        
        if result:
            return jsonify({
                'message': 'Entry created successfully',
                'entry': dict(result)
            }), 201
        else:
            return jsonify({
                'error': 'Database error',
                'message': 'Failed to create entry'
            }), 500
    except Exception as e:
        return jsonify({
            'error': 'Database error',
            'message': str(e)
        }), 500

@app.route('/api/entries/<int:entry_id>', methods=['GET'])
def get_entry(entry_id):
    """Get a specific entry by ID"""
    try:
        query = "SELECT * FROM entries WHERE id = %s;"
        result = db.execute_query(query, (entry_id,))
        if result:
            return jsonify(dict(result[0])), 200
        else:
            return jsonify({
                'error': 'Not found',
                'message': f'Entry with id {entry_id} not found'
            }), 404
    except Exception as e:
        return jsonify({
            'error': 'Database error',
            'message': str(e)
        }), 500

@app.route('/api/cron/run', methods=['POST', 'GET'])
def run_cron():
    """Manually trigger the cron job"""
    try:
        result = run_cron_job()
        
        if result['success']:
            return jsonify({
                'message': 'Cron job executed successfully',
                'result': result
            }), 200
        else:
            return jsonify({
                'message': 'Cron job executed with errors',
                'result': result
            }), 200
    except Exception as e:
        return jsonify({
            'error': 'Failed to execute cron job',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/test_db', methods=['GET'])
def get_test_db():
    """Get all entries from the test_db table"""
    try:
        query = "SELECT * FROM test_db ORDER BY sequence_number ASC;"
        results = db.execute_query(query)
        if results is not None:
            # Convert RealDictRow to dict for JSON serialization
            entries = [dict(row) for row in results]
            return jsonify({
                'entries': entries,
                'count': len(entries),
                'table': 'test_db'
            }), 200
        else:
            return jsonify({
                'entries': [],
                'count': 0,
                'table': 'test_db'
            }), 200
    except Exception as e:
        return jsonify({
            'error': 'Database error',
            'message': str(e)
        }), 500

@app.route('/api/companies', methods=['GET'])
def get_companies():
    """Get companies from the database"""
    try:
        # Get query parameters for pagination
        limit = request.args.get('limit', default=10, type=int)
        offset = request.args.get('offset', default=0, type=int)
        
        # Count total companies
        count_query = "SELECT COUNT(*) as total FROM companies;"
        count_result = db.execute_query(count_query)
        total = count_result[0]['total'] if count_result and len(count_result) > 0 else 0
        
        # Get companies with pagination
        query = """
        SELECT 
            id, organization_name, website, headquarters_location,
            cb_rank_company, founded_date, industries, description
        FROM companies 
        ORDER BY cb_rank_company ASC NULLS LAST
        LIMIT %s OFFSET %s;
        """
        results = db.execute_query(query, (limit, offset))
        
        if results is not None:
            companies = [dict(row) for row in results]
            return jsonify({
                'companies': companies,
                'count': len(companies),
                'total': total,
                'limit': limit,
                'offset': offset
            }), 200
        else:
            return jsonify({
                'companies': [],
                'count': 0,
                'total': 0
            }), 200
    except Exception as e:
        return jsonify({
            'error': 'Database error',
            'message': str(e)
        }), 500

@app.route('/api/companies/<int:company_id>', methods=['GET'])
def get_company(company_id):
    """Get a specific company by ID"""
    try:
        query = "SELECT * FROM companies WHERE id = %s;"
        result = db.execute_query(query, (company_id,))
        if result and len(result) > 0:
            return jsonify(dict(result[0])), 200
        else:
            return jsonify({
                'error': 'Not found',
                'message': f'Company with id {company_id} not found'
            }), 404
    except Exception as e:
        return jsonify({
            'error': 'Database error',
            'message': str(e)
        }), 500

@app.route('/api/companies/stats', methods=['GET'])
def get_company_stats():
    """Get statistics about companies in the database"""
    try:
        stats_query = """
        SELECT 
            COUNT(*) as total_companies,
            COUNT(DISTINCT website) as companies_with_websites,
            MIN(founded_date) as earliest_founded,
            MAX(founded_date) as latest_founded,
            AVG(total_funding_amount_usd) as avg_funding_usd
        FROM companies;
        """
        result = db.execute_query(stats_query)
        
        if result and len(result) > 0:
            return jsonify(dict(result[0])), 200
        else:
            return jsonify({
                'error': 'No statistics available'
            }), 404
    except Exception as e:
        return jsonify({
            'error': 'Database error',
            'message': str(e)
        }), 500

@app.route('/companies', methods=['GET'])
def view_companies():
    """Display companies table in browser with HTML"""
    try:
        # Get pagination parameters
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=50, type=int)
        offset = (page - 1) * per_page
        
        # Count total companies
        count_query = "SELECT COUNT(*) as total FROM companies;"
        count_result = db.execute_query(count_query)
        total = count_result[0]['total'] if count_result and len(count_result) > 0 else 0
        total_pages = (total + per_page - 1) // per_page
        
        # Get companies with pagination
        query = """
        SELECT 
            id, organization_name, website, headquarters_location,
            cb_rank_company, founded_date, industries, 
            total_funding_amount_usd, number_of_employees
        FROM companies 
        ORDER BY cb_rank_company ASC NULLS LAST
        LIMIT %s OFFSET %s;
        """
        results = db.execute_query(query, (per_page, offset))
        
        companies = []
        if results:
            for row in results:
                company = dict(row)
                # Format funding amount for display
                if company.get('total_funding_amount_usd'):
                    company['formatted_funding'] = f"${company['total_funding_amount_usd']:,.0f}"
                else:
                    company['formatted_funding'] = '-'
                companies.append(company)
        
        # HTML template
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Companies Database</title>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #f5f5f5;
                }
                .container {
                    max-width: 1400px;
                    margin: 0 auto;
                    background: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                h1 {
                    color: #333;
                    margin-bottom: 10px;
                }
                .stats {
                    background: #f8f9fa;
                    padding: 15px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                    display: flex;
                    gap: 30px;
                    flex-wrap: wrap;
                }
                .stat-item {
                    display: flex;
                    flex-direction: column;
                }
                .stat-label {
                    font-size: 12px;
                    color: #666;
                    text-transform: uppercase;
                }
                .stat-value {
                    font-size: 24px;
                    font-weight: bold;
                    color: #333;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                }
                th {
                    background-color: #4a90e2;
                    color: white;
                    padding: 12px;
                    text-align: left;
                    font-weight: 600;
                    position: sticky;
                    top: 0;
                }
                td {
                    padding: 10px 12px;
                    border-bottom: 1px solid #e0e0e0;
                }
                tr:hover {
                    background-color: #f8f9fa;
                }
                .website-link {
                    color: #4a90e2;
                    text-decoration: none;
                }
                .website-link:hover {
                    text-decoration: underline;
                }
                .pagination {
                    margin-top: 20px;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    gap: 10px;
                }
                .pagination a, .pagination span {
                    padding: 8px 12px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    text-decoration: none;
                    color: #333;
                }
                .pagination a:hover {
                    background-color: #f0f0f0;
                }
                .pagination .current {
                    background-color: #4a90e2;
                    color: white;
                    border-color: #4a90e2;
                }
                .pagination .disabled {
                    color: #ccc;
                    cursor: not-allowed;
                }
                .funding {
                    color: #28a745;
                    font-weight: 500;
                }
                .rank {
                    font-weight: bold;
                    color: #4a90e2;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Companies Database</h1>
                <div class="stats">
                    <div class="stat-item">
                        <span class="stat-label">Total Companies</span>
                        <span class="stat-value">{{ total }}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Page</span>
                        <span class="stat-value">{{ page }} / {{ total_pages }}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Showing</span>
                        <span class="stat-value">{{ showing_count }} companies</span>
                    </div>
                </div>
                
                <table>
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Company Name</th>
                            <th>Website</th>
                            <th>Location</th>
                            <th>Industries</th>
                            <th>Founded</th>
                            <th>Employees</th>
                            <th>Total Funding (USD)</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for company in companies %}
                        <tr>
                            <td class="rank">{{ company.cb_rank_company or '-' }}</td>
                            <td><strong>{{ company.organization_name }}</strong></td>
                            <td>
                                {% if company.website %}
                                <a href="{{ company.website }}" target="_blank" class="website-link">
                                    {{ company.website[:40] }}{% if company.website|length > 40 %}...{% endif %}
                                </a>
                                {% else %}
                                -
                                {% endif %}
                            </td>
                            <td>{{ company.headquarters_location or '-' }}</td>
                            <td>{{ company.industries[:50] if company.industries else '-' }}{% if company.industries and company.industries|length > 50 %}...{% endif %}</td>
                            <td>{{ company.founded_date.strftime('%Y-%m-%d') if company.founded_date else '-' }}</td>
                            <td>{{ company.number_of_employees or '-' }}</td>
                            <td class="funding">{{ company.formatted_funding }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                
                <div class="pagination">
                    {% if page > 1 %}
                    <a href="?page={{ page - 1 }}&per_page={{ per_page }}">Previous</a>
                    {% else %}
                    <span class="disabled">Previous</span>
                    {% endif %}
                    
                    {% for p in range(1, total_pages + 1) %}
                        {% if p == page %}
                        <span class="current">{{ p }}</span>
                        {% elif p <= 3 or p > total_pages - 3 or (p >= page - 1 and p <= page + 1) %}
                        <a href="?page={{ p }}&per_page={{ per_page }}">{{ p }}</a>
                        {% elif p == 4 or p == total_pages - 3 %}
                        <span>...</span>
                        {% endif %}
                    {% endfor %}
                    
                    {% if page < total_pages %}
                    <a href="?page={{ page + 1 }}&per_page={{ per_page }}">Next</a>
                    {% else %}
                    <span class="disabled">Next</span>
                    {% endif %}
                </div>
            </div>
        </body>
        </html>
        """
        
        return render_template_string(
            html_template,
            companies=companies,
            total=total,
            page=page,
            total_pages=total_pages,
            showing_count=len(companies)
        ), 200
        
    except Exception as e:
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    padding: 40px;
                    text-align: center;
                }}
                .error {{
                    color: #d32f2f;
                    background: #ffebee;
                    padding: 20px;
                    border-radius: 5px;
                    display: inline-block;
                }}
            </style>
        </head>
        <body>
            <div class="error">
                <h2>Database Error</h2>
                <p>{str(e)}</p>
            </div>
        </body>
        </html>
        """
        return render_template_string(error_html), 500

@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested resource was not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'Something went wrong!' if app.config['ENV'] == 'production' else str(error)
    }), 500

@app.teardown_appcontext
def close_db(error):
    """Close database connections when app context is torn down."""
    pass  # Connection pool handles connections automatically

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=app.config['PORT'], debug=app.config['DEBUG'])

