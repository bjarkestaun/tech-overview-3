"""Configuration settings for the application."""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration."""
    PORT = int(os.environ.get('PORT', 5000))
    ENV = os.environ.get('ENV', 'development')
    DEBUG = ENV == 'development'
    
    # Database configuration - must be set as environment variable
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is required")

