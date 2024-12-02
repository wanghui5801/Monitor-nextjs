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
        "allow_headers": ["Content-Type"],
        "expose_headers": ["Content-Type"]
    }
})
app.config.from_object(Config)

# 注册蓝图
app.register_blueprint(api, url_prefix='/api')

# 初始化数据库
server_model = Server(Config.DATABASE_PATH)
try:
    server_model.init_db()
except Exception as e:
    print(f"Database initialization error: {e}")

servers = {}  # 使用字典存储服务器信息，key 为 server_id

# 创建定时任务调度器
scheduler = BackgroundScheduler()
scheduler.start()

# 添加定时任务，每5秒检查一次服务器状态
scheduler.add_job(
    func=server_model.check_inactive_servers,
    trigger=IntervalTrigger(seconds=5),
    id='check_server_status',
    name='Check server status',
    replace_existing=True
)

# 确保在应用退出时关闭调度器
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
    
    # 获取当前服务器状态
    current_server = servers.get(server_id, {})
    current_status = current_server.get('status', 'running')
    
    # 如果状态不是 running，返回最后一次的数据
    if current_status != 'running':
        if current_server:
            return jsonify(current_server)
        return jsonify({'error': 'Server not found'}), 404
    
    # 状态为 running 时更新数据
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

if __name__ == '__main__':
    app.run(debug=Config.DEBUG, host='0.0.0.0')
