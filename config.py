"""Configuration settings for the application."""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration."""
    PORT = int(os.environ.get('PORT', 5000))
    ENV = os.environ.get('ENV', 'development')
    DEBUG = ENV == 'development'
    
    # Database configuration
    DATABASE_URL = os.environ.get(
        'DATABASE_URL',
        'postgresql://techstack_4vkf_user:E3YrawtrX14MgEJinDqr0qwtuo6iWWDC@dpg-d3eo5jadbo4c73bgtrfg-a.frankfurt-postgres.render.com/techstack_4vkf'
    )

