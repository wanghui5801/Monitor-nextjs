from flask import Blueprint, request, jsonify
from models.server import Server
from config import Config
from datetime import datetime

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
            
        # 更新服务器状态
        server_model.update_server({
            'id': server_id,
            'status': new_status
        })
        
        # 获取更新后的服务器数据
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
        if not data or 'id' not in data or 'name' not in data:
            return jsonify({'error': 'Invalid data'}), 400
            
        # 检查客户端是否被允许
        if not server_model.is_client_allowed(data['name']):
            return jsonify({'error': 'Client not allowed'}), 403
            
        # 获取服务器当前状态
        conn = server_model.get_db()
        c = conn.cursor()
        try:
            c.execute('SELECT status, order_index FROM servers WHERE id = ?', (data['id'],))
            result = c.fetchone()
            
            if result:
                current_status, order_index = result
                # 如果当前状态是stopped且不是maintenance状态，则改为running
                if current_status == 'stopped' and current_status != 'maintenance':
                    current_status = 'running'
            else:
                # 新服务器首次连接时设为running
                current_status = 'running'
                c.execute('SELECT COALESCE(MIN(order_index) - 1, 0) FROM servers')
                order_index = c.fetchone()[0]
            
            # 更新服务器数据
            data['status'] = current_status
            data['order_index'] = order_index
            server_model.update_server(data)
            
            return jsonify({'status': 'success'}), 200
            
        finally:
            conn.close()
            
    except Exception as e:
        print(f"Error updating server: {e}")
        return jsonify({'error': str(e)}), 500

@api.route('/servers', methods=['GET'])
def get_servers():
    try:
        # 先检查非活动服务器
        server_model.check_inactive_servers()
        
        # 然后获取服务器列表
        conn = server_model.get_db()
        c = conn.cursor()
        try:
            c.execute('''
                WITH RankedServers AS (
                    SELECT *,
                           ROW_NUMBER() OVER (PARTITION BY id ORDER BY last_update DESC) as rn
                    FROM servers
                )
                SELECT id, name, type, location, status, uptime, 
                       network_in, network_out, cpu, memory, disk, 
                       os_type, order_index, first_seen, last_update
                FROM RankedServers
                WHERE rn = 1
                ORDER BY order_index DESC NULLS LAST, first_seen ASC
            ''')
            
            columns = [description[0] for description in c.description]
            servers = []
            for row in c.fetchall():
                server_dict = dict(zip(columns, row[:-1]))  # 排除 rn 列
                servers.append(server_dict)
            
            return jsonify(servers)
        finally:
            conn.close()
    except Exception as e:
        print(f"Error getting servers: {e}")
        return jsonify([])

@api.route('/servers/<server_id>', methods=['GET'])
def get_server_status(server_id):
    try:
        conn = server_model.get_db()
        c = conn.cursor()
        c.execute('SELECT * FROM servers WHERE id = ? ORDER BY last_update DESC LIMIT 1', (server_id,))
        server_data = c.fetchone()
        
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
        # 获取服务器名称
        conn = server_model.get_db()
        c = conn.cursor()
        try:
            c.execute('SELECT name FROM servers WHERE id = ?', (server_id,))
            result = c.fetchone()
            if result:
                client_name = result[0]
                # 删除服务器记录
                server_model.delete_server(server_id)
                # 删除允许的客户端
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
            
        server_model.add_allowed_client(data['name'])
        return jsonify({'status': 'success'}), 200
            
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
