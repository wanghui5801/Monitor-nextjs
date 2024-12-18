from flask import Blueprint, request, jsonify
from models.server import Server
from config import Config
from datetime import datetime
import sqlite3

api = Blueprint('api', __name__)
server_model = Server(Config.DATABASE_PATH)

@api.route('/servers/<server_id>/status', methods=['PUT', 'OPTIONS'])
def update_server_status(server_id):
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        data = request.json
        new_status = data.get('status')
        
        if not new_status:
            return jsonify({'error': 'Status is required'}), 400
            
        if new_status not in ['running', 'stopped', 'maintenance']:
            return jsonify({'error': 'Invalid status'}), 400
            
        # Update server status
        server_model.update_server({
            'id': server_id,
            'status': new_status
        })
        
        # Get updated server data
        conn = server_model.get_db()
        c = conn.cursor()
        try:
            c.execute('SELECT * FROM servers WHERE id = ? ORDER BY last_update DESC LIMIT 1', (server_id,))
            server_data = c.fetchone()
            if server_data:
                columns = [description[0] for description in c.description]
                return jsonify(dict(zip(columns, server_data)))
        finally:
            conn.close()
            
        return jsonify({'error': 'Server not found'}), 404
            
    except Exception as e:
        print(f"Error updating server status: {e}")
        return jsonify({'error': str(e)}), 500

@api.route('/servers/update', methods=['POST'])
def update_server():
    try:
        data = request.json
        print(f"Received update data: {data}")
        
        if not data or 'id' not in data or 'name' not in data:
            return jsonify({'error': 'Invalid data'}), 400
            
        # Check if the client is allowed
        if not server_model.is_client_allowed(data['name']):
            return jsonify({'error': 'Client not allowed'}), 403
            
        # Get current server status
        conn = server_model.get_db()
        c = conn.cursor()
        try:
            c.execute('SELECT status, order_index FROM servers WHERE id = ?', (data['id'],))
            result = c.fetchone()
            
            if result:
                current_status, order_index = result
                # Update status based on current state
                if current_status in ['maintenance', 'stopped']:
                    data['status'] = 'running'
                elif current_status == 'running':
                    data['status'] = 'running'  # Maintain running status
                data['order_index'] = order_index
            else:
                # New server first connection
                data['status'] = 'running'
                c.execute('SELECT COALESCE(MAX(order_index), 0) FROM servers')
                data['order_index'] = c.fetchone()[0] - 1
            
            server_model.update_server(data)
            return jsonify({'status': 'success'}), 200
            
        finally:
            conn.close()
            
    except Exception as e:
        print(f"Error in update_server: {e}")
        return jsonify({'error': str(e)}), 500

@api.route('/servers', methods=['GET'])
def get_servers():
    try:
        conn = server_model.get_db()
        c = conn.cursor()
        c.execute('''
            SELECT id, name, type, location, status, uptime, 
                   network_in, network_out, cpu, memory, disk, 
                   os_type, cpu_info, total_memory, total_disk, 
                   ip_address, order_index
            FROM servers 
            ORDER BY order_index DESC
        ''')
        servers = c.fetchall()
        columns = [description[0] for description in c.description]
        
        # 检查是否有认证token
        auth_header = request.headers.get('Authorization')
        is_authenticated = False
        if auth_header:
            try:
                token = auth_header.split(' ')[1]
                if server_model.verify_token(token):
                    is_authenticated = True
            except:
                pass
        
        # Convert to list of dictionaries
        result = []
        for server in servers:
            server_dict = dict(zip(columns, server))
            # 对未认证的请求隐藏IP地址
            if not is_authenticated:
                server_dict['ip_address'] = '***.***.***.**'
            result.append(server_dict)
            
        return jsonify(result)
    except Exception as e:
        print(f"Error getting servers: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@api.route('/servers/<server_id>', methods=['GET'])
def get_server_status(server_id):
    try:
        conn = server_model.get_db()
        c = conn.cursor()
        c.execute('SELECT * FROM servers WHERE id = ? ORDER BY last_update DESC LIMIT 1', (server_id,))
        server_data = c.fetchone()
        columns = [description[0] for description in c.description]
        if not server_data:
            return jsonify({'error': 'Server not found'}), 404
            
        columns = [description[0] for description in c.description]
        server_dict = dict(zip(columns, server_data))
        return jsonify(server_dict)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@api.route('/servers/<server_id>/order', methods=['PUT'])
def update_server_order(server_id):
    try:
        data = request.json
        order_index = data.get('order_index')
        
        if order_index is None:
            return jsonify({'error': 'Order index is required'}), 400
            
        conn = server_model.get_db()
        c = conn.cursor()
        
        try:
            c.execute('''
                UPDATE servers 
                SET order_index = ? 
                WHERE id = ?
            ''', (order_index, server_id))
            conn.commit()
            
            return jsonify({'status': 'success'}), 200
        finally:
            conn.close()
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/servers/<server_id>', methods=['DELETE'])
def delete_server(server_id):
    try:
        # Get server name
        conn = server_model.get_db()
        c = conn.cursor()
        try:
            c.execute('SELECT name FROM servers WHERE id = ?', (server_id,))
            result = c.fetchone()
            if result:
                client_name = result[0]
                # Delete server record
                server_model.delete_server(server_id)
                # Delete allowed client
                server_model.delete_allowed_client(client_name)
                return jsonify({'status': 'success'}), 200
            return jsonify({'error': 'Server not found'}), 404
        finally:
            conn.close()
    except Exception as e:
        print(f"Error deleting server: {e}")
        return jsonify({'error': str(e)}), 500

@api.route('/clients', methods=['POST'])
def add_client():
    try:
        data = request.json
        if not data or 'name' not in data:
            return jsonify({'error': 'Client name is required'}), 400
            
        # Check if the client name already exists
        conn = server_model.get_db()
        c = conn.cursor()
        try:
            c.execute('SELECT name FROM allowed_clients WHERE name = ?', (data['name'],))
            if c.fetchone():
                return jsonify({'error': 'Client already exists'}), 400
                
            # Add new client
            server_model.add_allowed_client(data['name'])
            return jsonify({'status': 'success'}), 200
        finally:
            conn.close()
            
    except Exception as e:
        print(f"Error adding client: {e}")
        return jsonify({'error': str(e)}), 500

@api.route('/clients', methods=['GET'])
def get_clients():
    try:
        conn = server_model.get_db()
        c = conn.cursor()
        try:
            c.execute('SELECT name, created_at FROM allowed_clients')
            clients = [{'name': row[0], 'created_at': row[1]} for row in c.fetchall()]
            return jsonify(clients), 200
        finally:
            conn.close()
    except Exception as e:
        print(f"Error getting clients: {e}")
        return jsonify({'error': str(e)}), 500

@api.route('/auth/reset-password', methods=['POST', 'OPTIONS'])
def reset_password():
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
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
        
    except Exception as e:
        print(f"Error resetting password: {e}")
        return jsonify({'error': str(e)}), 500

@api.route('/servers/<server_id>/heartbeat', methods=['POST'])
def server_heartbeat(server_id):
    """Lightweight heartbeat endpoint"""
    try:
        conn = server_model.get_db()
        c = conn.cursor()
        try:
            current_time = datetime.now().isoformat()
            c.execute('''
                UPDATE servers 
                SET last_update = ?, status = 'running'
                WHERE id = ? AND status != 'maintenance'
            ''', (current_time, server_id))
            conn.commit()
            return jsonify({'status': 'success'}), 200
        finally:
            conn.close()
    except Exception as e:
        print(f"Error in heartbeat: {e}")
        return jsonify({'error': str(e)}), 500
