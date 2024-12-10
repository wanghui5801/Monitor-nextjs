from flask import Flask, request, jsonify
from flask_cors import CORS
from routes.api import api
from models.server import Server
from config import Config
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import atexit
import jwt
import sqlite3
import os
from flask_socketio import SocketIO, emit
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})
app.config.from_object(Config)

# Register blueprint
app.register_blueprint(api, url_prefix='/api')

# Initialize database
server_model = Server(Config.DATABASE_PATH)
try:
    server_model.init_db()
    print("Database initialized successfully")
except Exception as e:
    print(f"Database initialization error: {e}")
    exit(1)  # Exit if database initialization fails

servers = {}  # Use dictionary to store server information, key is server_id

# Create scheduled task scheduler
scheduler = BackgroundScheduler()
scheduler.start()

# Add scheduled task, check server status every 30 seconds
scheduler.add_job(
    func=server_model.check_server_status,
    trigger=IntervalTrigger(seconds=30),
    id='check_server_status',
    name='Check server status',
    replace_existing=True
)

# Ensure scheduler is shut down when application exits
atexit.register(lambda: scheduler.shutdown())

@app.route('/api/servers/<server_id>/status', methods=['PUT'])
def update_server_status(server_id):
    if server_id not in servers:
        return jsonify({'error': 'Server not found'}), 404
        
    data = request.json
    new_status = data.get('status')
    
    if new_status not in ['running', 'stopped', 'maintenance', 'waiting']:
        return jsonify({'error': 'Invalid status'}), 400
        
    servers[server_id]['status'] = new_status
    servers[server_id]['last_update'] = datetime.now().isoformat()
    
    return jsonify(servers[server_id])

@app.route('/api/servers/update', methods=['POST'])
def update_server():
    data = request.json
    server_id = data.get('id')
    
    if not server_id:
        return jsonify({'error': 'Server ID required'}), 400
    
    # Get current server status
    current_server = servers.get(server_id, {})
    current_status = current_server.get('status', 'running')
    
    # If status is not running, return the last data
    if current_status != 'running':
        if current_server:
            return jsonify(current_server)
        return jsonify({'error': 'Server not found'}), 404
    
    # Update data when status is running
    servers[server_id] = {**data, 'status': current_status, 'last_update': datetime.now().isoformat()}
    return jsonify(servers[server_id])

@app.route('/api/auth/status', methods=['GET'])
def auth_status():
    return jsonify({'initialized': server_model.is_initialized()})

@app.route('/api/auth/initialize', methods=['POST'])
def initialize_auth():
    if server_model.is_initialized():
        return jsonify({'error': 'Already initialized'}), 400
    
    data = request.get_json()
    password = data.get('password')
    if not password:
        return jsonify({'error': 'Password is required'}), 400
        
    success = server_model.set_admin_password(password)
    return jsonify({'success': success})

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    password = data.get('password')
    if not password:
        return jsonify({'error': 'Password is required'}), 400
        
    if server_model.verify_password(password):
        token = jwt.encode({'exp': datetime.utcnow() + timedelta(days=1)}, 
                         app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({'token': token})
    return jsonify({'error': 'Invalid password'}), 401

@app.route('/api/auth/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    old_password = data.get('oldPassword')
    new_password = data.get('newPassword')
    
    if not old_password or not new_password:
        return jsonify({'error': 'Both old and new passwords are required'}), 400
        
    # Verify old password
    if not server_model.verify_password(old_password):
        return jsonify({'error': 'Current password is incorrect'}), 401
        
    # Set new password
    success = server_model.set_admin_password(new_password)
    return jsonify({'success': success})

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='threading',
    ping_timeout=60,
    ping_interval=25,
    logger=True,
   engineio_logger=True,
    max_http_buffer_size=1000000,
    manage_session=False,
    always_connect=True,
    websocket_ping_interval=25,
    websocket_ping_timeout=60
)

# Store client last update time
client_last_update = {}

@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")
    
@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")
    if hasattr(request, 'client_name'):
        print(f"Client {request.client_name} disconnected")

@socketio.on('server_update')
def handle_server_update(data):
    try:
        if not data or 'id' not in data or 'name' not in data:
            return
            
        request.client_name = data['name']
        
        server_model.update_last_activity(data['name'])
        
        data['status'] = 'running'
        server_model.update_server(data)
        
        emit('server_status_update', data, broadcast=True)
    except Exception as e:
        print(f"Error handling server update: {e}")

def check_inactive_clients():
    """Check inactive clients"""
    try:
        server_model.check_inactive_servers()
    except Exception as e:
        print(f"Error checking inactive clients: {e}")

# Configure logging
logging.basicConfig(
    handlers=[RotatingFileHandler(
        'server-monitor.log', 
        maxBytes=10000000, 
        backupCount=5
    )],
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)

# 添加错误处理
@socketio.on_error()
def error_handler(e):
    print(f"SocketIO error: {e}")
    
@socketio.on_error_default
def default_error_handler(e):
    print(f"SocketIO default error: {e}")

if __name__ == '__main__':
    try:
        print("Starting server in production mode...")
        socketio.run(
            app,
            host='0.0.0.0',
            port=5000,
            debug=False,
            use_reloader=False,
            allow_unsafe_werkzeug=True
        )
    except Exception as e:
        print(f"Error starting server: {e}")
