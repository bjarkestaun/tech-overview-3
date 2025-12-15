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
DATABASE_URL=your-database-connection-string-here
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

### Cron Job
- `GET /api/cron/run` - Manually trigger the cron job
- `POST /api/cron/run` - Manually trigger the cron job (same as GET)
- `GET /api/test_db` - Get all entries from the test_db table

## Deployment to Render

### Option 1: Using render.yaml (Recommended)

1. Push your code to GitHub (already done)
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click "New +" and select "Blueprint"
4. Connect your GitHub repository
5. Render will automatically detect the `render.yaml` file and deploy

**Note:** If the cron job doesn't appear or doesn't run after Blueprint deployment, you may need to create it manually (see Option 2 below). Some users report that cron jobs need to be created manually in the Render dashboard even when using Blueprints.

### Option 2: Manual Setup

#### Web Service:
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" and select "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: tech-overview-3
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Health Check Path**: `/health`
5. Add environment variables (see "Environment Variables" section below):
   - `ENV` = `production`
   - `DATABASE_URL` = (get from your database service's Connect tab)
6. Click "Create Web Service"

#### Cron Job (Manual Setup - Recommended if Blueprint doesn't work):
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" and select "Cron Job"
3. Connect your GitHub repository: `tech-overview-3`
4. Configure:
   - **Name**: `tech-overview-3-cron`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Schedule**: `0 0 * * *` (every day at midnight UTC)
   - **Command**: `python3 cron_job.py`
5. Add environment variables (see "Environment Variables" section below):
   - `ENV` = `production`
   - `DATABASE_URL` = (get from your database service's Connect tab)
6. Click "Create Cron Job"
7. **Important**: After creation, go to the cron job page and click "Trigger Run" to test it immediately

## Environment Variables

### Local Development

Create a `.env` file for local development:
```
PORT=5000
ENV=development
DATABASE_URL=your-database-connection-string-here
```

### Render Deployment

**Important**: You must set the `DATABASE_URL` environment variable in Render's dashboard:

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Navigate to your **Web Service** (`tech-overview-3`)
3. Click on the service name
4. Go to the **"Environment"** tab (in the left sidebar)
5. Click **"Add Environment Variable"**
6. Set:
   - **Key**: `DATABASE_URL`
   - **Value**: Your PostgreSQL connection string (get this from your database service's "Connect" tab)
7. Click **"Save Changes"**

**Repeat the same steps for your Cron Job service** (`tech-overview-3-cron`) to add the `DATABASE_URL` there as well.

**To get your database connection string:**
1. Go to your PostgreSQL database service in Render
2. Click on the database name
3. Go to the **"Connect"** tab
4. Copy the **"Internal Database URL"** or **"External Database URL"**
5. Use this as your `DATABASE_URL` value

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

The application uses PostgreSQL with connection pooling for efficient database operations. The database automatically creates the following tables on first startup:

### entries table (for API)
- `id` - Serial primary key
- `title` - VARCHAR(255)
- `content` - TEXT
- `created_at` - TIMESTAMP (auto-generated)

### test_db table (for cron job)
- `id` - Serial primary key
- `sequence_number` - INTEGER (sequential number for each cron run)
- `run_timestamp` - TIMESTAMP (when the cron job executed)

## Cron Job

The application includes a scheduled cron job that runs every 24 hours at midnight UTC. The cron job is configured in `render.yaml` and performs:

- Adds an entry to the `test_db` table with a sequential number and timestamp
- Each entry contains:
  - `sequence_number`: Sequential number (increments with each run)
  - `run_timestamp`: Timestamp of when the cron job executed
- Tracks total entries in the `test_db` table

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

### Troubleshooting Cron Job

If the cron job isn't running on Render:

1. **Check Render Logs**: Go to your Render dashboard → Cron Job → Logs to see execution logs
2. **Verify Schedule**: Ensure the cron schedule `0 0 * * *` is correct (midnight UTC daily)
3. **Test Manually**: Use the `/api/cron/run` endpoint to manually trigger the job and verify it works
4. **Check Database Connection**: Verify the `DATABASE_URL` environment variable is set correctly in Render
5. **View Logs**: The cron job now includes verbose logging with `flush=True` to ensure all output is captured in Render logs

The cron job script has been improved with:
- Explicit environment variable loading
- Better error handling and logging
- Database connection verification
- Detailed tracebacks for debugging

