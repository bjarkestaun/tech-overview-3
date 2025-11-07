# Tech Overview 3

A Python web service scaffold ready for deployment to Render.

## Features

- Flask web framework
- PostgreSQL database integration with connection pooling
- Health check endpoint for Render monitoring
- Environment variable configuration
- Error handling
- Render deployment configuration
- Gunicorn WSGI server for production
- RESTful API endpoints for database operations
- Scheduled cron job (runs every 24 hours)

## Local Development

1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file:
```bash
PORT=5000
ENV=development
DATABASE_URL=postgresql://techstack_4vkf_user:E3YrawtrX14MgEJinDqr0qwtuo6iWWDC@dpg-d3eo5jadbo4c73bgtrfg-a/techstack_4vkf
```

4. Run the development server:
```bash
python app.py
```

Or use Flask's development server:
```bash
flask run
```

The server will run on `http://localhost:5000`

## API Endpoints

### General
- `GET /` - Welcome message
- `GET /health` - Health check endpoint (used by Render)
- `GET /api/status` - API status information

### Database
- `GET /api/db/test` - Test database connection
- `GET /api/entries` - Get all entries (limit 100)
- `POST /api/entries` - Create a new entry
  - Body: `{"title": "Entry Title", "content": "Entry content"}`
- `GET /api/entries/<id>` - Get a specific entry by ID

## Deployment to Render

### Option 1: Using render.yaml (Recommended)

1. Push your code to GitHub (already done)
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click "New +" and select "Blueprint"
4. Connect your GitHub repository
5. Render will automatically detect the `render.yaml` file and deploy

### Option 2: Manual Setup

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" and select "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: tech-overview-3
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Health Check Path**: `/health`
5. Add environment variables if needed
6. Click "Create Web Service"

## Environment Variables

Create a `.env` file for local development:
```
PORT=5000
ENV=development
DATABASE_URL=postgresql://techstack_4vkf_user:E3YrawtrX14MgEJinDqr0qwtuo6iWWDC@dpg-d3eo5jadbo4c73bgtrfg-a/techstack_4vkf
```

For Render, the `DATABASE_URL` is configured in `render.yaml`. You can override it in the Render dashboard if needed.

## Project Structure

```
.
├── app.py            # Main Flask application
├── config.py         # Configuration settings
├── db.py             # Database connection and utilities
├── cron_job.py       # Scheduled cron job script
├── requirements.txt  # Python dependencies
├── render.yaml       # Render deployment configuration
├── runtime.txt       # Python version for Render
├── .python-version   # Python version (optional)
├── .gitignore       # Git ignore rules
└── README.md        # This file
```

## Requirements

- Python 3.11+
- Flask 3.0.0
- Gunicorn (for production deployment)
- PostgreSQL database (configured on Render)
- psycopg2-binary (PostgreSQL adapter)

## Database

The application uses PostgreSQL with connection pooling for efficient database operations. The database automatically creates an `entries` table on first startup with the following schema:

- `id` - Serial primary key
- `title` - VARCHAR(255)
- `content` - TEXT
- `created_at` - TIMESTAMP (auto-generated)

## Cron Job

The application includes a scheduled cron job that runs every 24 hours at midnight UTC. The cron job is configured in `render.yaml` and performs:

- Database cleanup (removes entries older than 30 days)
- Database statistics collection
- Custom maintenance tasks (customize in `cron_job.py`)

### Cron Job Schedule

The cron job runs on the schedule defined in `render.yaml`:
- **Schedule**: `0 0 * * *` (every day at midnight UTC)
- **Command**: `python cron_job.py`

You can customize the cron job schedule using standard cron syntax:
- `0 0 * * *` - Every day at midnight
- `0 */6 * * *` - Every 6 hours
- `0 0 * * 0` - Every Sunday at midnight

### Local Testing

To test the cron job locally:
```bash
python cron_job.py
```

The cron job will connect to your database and execute the scheduled tasks.

