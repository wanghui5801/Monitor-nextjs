import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'servers.db')
    DEBUG = True
    CORS_HEADERS = 'Content-Type'
