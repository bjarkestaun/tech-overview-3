from datetime import datetime
from flask import Flask, jsonify, request
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

