from datetime import datetime
from flask import Flask, jsonify
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=app.config['PORT'], debug=app.config['DEBUG'])

