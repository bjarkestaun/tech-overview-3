# Tech Overview 3

A Python web service scaffold ready for deployment to Render.

## Features

- Flask web framework
- Health check endpoint for Render monitoring
- Environment variable configuration
- Error handling
- Render deployment configuration
- Gunicorn WSGI server for production

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

- `GET /` - Welcome message
- `GET /health` - Health check endpoint (used by Render)
- `GET /api/status` - API status information

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
```

For Render, add environment variables in the Render dashboard or in `render.yaml`.

## Project Structure

```
.
├── app.py            # Main Flask application
├── config.py         # Configuration settings
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

