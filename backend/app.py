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
except Exception as e:
    print(f"Database initialization error: {e}")

servers = {}  # Use dictionary to store server information, key is server_id

# Create scheduled task scheduler
scheduler = BackgroundScheduler()
scheduler.start()

# Add scheduled task, check server status every 5 seconds
scheduler.add_job(
    func=server_model.check_inactive_servers,
    trigger=IntervalTrigger(seconds=5),
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
    if success:
        # Generate token after successful initialization
        token = jwt.encode(
            {'exp': datetime.utcnow() + timedelta(days=1)}, 
            app.config['SECRET_KEY'], 
            algorithm='HS256'
        )
        return jsonify({'token': token, 'success': True})
    return jsonify({'error': 'Failed to initialize'}), 500

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

if __name__ == '__main__':
    app.run(debug=Config.DEBUG, host='0.0.0.0')
