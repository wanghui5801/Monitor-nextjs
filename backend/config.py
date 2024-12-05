import os
from dotenv import load_dotenv
import socket

load_dotenv()

def get_server_ip():
    try:
        import requests
        ip = requests.get('https://api.ipify.org').text
    except:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        except:
            ip = '127.0.0.1'
        finally:
            s.close()
    return ip

SERVER_IP = os.getenv('SERVER_IP', get_server_ip())

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'servers.db')
    DEBUG = False
    CORS_HEADERS = 'Content-Type'
