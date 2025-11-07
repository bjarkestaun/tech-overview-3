"""Configuration settings for the application."""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration."""
    PORT = int(os.environ.get('PORT', 5000))
    ENV = os.environ.get('ENV', 'development')
    DEBUG = ENV == 'development'
    
    # Add your configuration variables here
    # DATABASE_URL = os.environ.get('DATABASE_URL')
    # API_KEY = os.environ.get('API_KEY')

