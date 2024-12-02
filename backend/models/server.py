from datetime import datetime
import sqlite3
from typing import Dict, List
import bcrypt

class Server:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
            # 创建表（如果不存在）
            c.execute('''
                CREATE TABLE IF NOT EXISTS servers (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    type TEXT,
                    location TEXT,
                    status TEXT DEFAULT 'stopped',
                    uptime INTEGER,
                    network_in REAL,
                    network_out REAL,
                    cpu REAL,
                    memory REAL,
                    disk REAL,
                    os_type TEXT,
                    order_index INTEGER DEFAULT 0,
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 将所有running状态的服务器改为stopped
            c.execute('''
                UPDATE servers 
                SET status = 'stopped' 
                WHERE status = 'running'
            ''')
            
            # 创建允许的客户端表
            c.execute('''
                CREATE TABLE IF NOT EXISTS allowed_clients (
                    name TEXT PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建管理员认证表
            c.execute('''
                CREATE TABLE IF NOT EXISTS admin_auth (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    password_hash TEXT NOT NULL,
                    is_initialized BOOLEAN DEFAULT FALSE
                )
            ''')
            conn.commit()
        finally:
            conn.close()

    def get_all_servers(self) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT * FROM servers')
        columns = [description[0] for description in c.description]
        servers = []
        for row in c.fetchall():
            server = dict(zip(columns, row))
            servers.append(server)
        conn.close()
        return servers

    def update_server(self, server_data: Dict):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
            # 检查服务器是否存在并获取当前状态和order_index
            c.execute('SELECT status, order_index FROM servers WHERE id = ?', (server_data['id'],))
            result = c.fetchone()
            
            if not result:
                # 新服务器 - 获取最小的order_index
                c.execute('SELECT COALESCE(MIN(order_index) - 1, 0) FROM servers')
                order_index = c.fetchone()[0]
                current_status = 'running'
            else:
                current_status, order_index = result
            
            # 使用 REPLACE INTO 来更新或插入记录
            c.execute('''
                REPLACE INTO servers 
                (id, name, type, location, status, uptime, network_in, network_out,
                 cpu, memory, disk, os_type, order_index, last_update)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                server_data['id'],
                server_data.get('name', ''),
                server_data.get('type', ''),
                server_data.get('location', ''),
                current_status,
                server_data.get('uptime', 0),
                server_data.get('network_in', 0),
                server_data.get('network_out', 0),
                server_data.get('cpu', 0),
                server_data.get('memory', 0),
                server_data.get('disk', 0),
                server_data.get('os_type', ''),
                order_index
            ))
            conn.commit()
        finally:
            conn.close()

    def get_db(self):
        return sqlite3.connect(self.db_path)

    def get_latest_servers(self) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
            c.execute('''
                SELECT id, name, type, location, status, uptime, 
                       network_in, network_out, cpu, memory, disk, 
                       os_type, order_index, first_seen, last_update
                FROM servers
                ORDER BY order_index DESC, first_seen ASC
            ''')
            
            columns = [description[0] for description in c.description]
            servers = []
            for row in c.fetchall():
                server_dict = dict(zip(columns, row))
                servers.append(server_dict)
            
            return servers
        finally:
            conn.close()

    def get_next_order_index(self):
        conn = self.get_db()
        c = conn.cursor()
        try:
            c.execute('SELECT MAX(order_index) FROM servers')
            result = c.fetchone()
            return (result[0] or 0) + 1
        finally:
            conn.close()

    def update_server_order(self, server_id: str, order_index: int):
        conn = self.get_db()
        c = conn.cursor()
        try:
            c.execute('''
                UPDATE servers 
                SET order_index = ?
                WHERE id = ?
            ''', (order_index, server_id))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating server order: {e}")
            return False
        finally:
            conn.close()

    def check_server_status(self):
        """检查所有服务器状态，将超时的服务器标记为stopped"""
        conn = self.get_db()
        c = conn.cursor()
        try:
            current_time = datetime.now()
            c.execute('''
                UPDATE servers
                SET status = 'stopped'
                WHERE id IN (
                    SELECT id FROM servers 
                    WHERE status = 'running' 
                    AND (strftime('%s', ?) - strftime('%s', last_update)) > 30
                )
            ''', (current_time.isoformat(),))
            conn.commit()
        finally:
            conn.close()

    def check_inactive_servers(self):
        """检查所有服务器状态，将超过5秒未更新的服务器标记为stopped"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
            current_time = datetime.now()
            
            # 更新超过5秒未更新且状态为running的服务器状态为stopped
            c.execute('''
                UPDATE servers
                SET status = 'stopped'
                WHERE id IN (
                    SELECT id FROM servers 
                    WHERE status = 'running'
                    AND status != 'maintenance'
                    AND datetime(last_update) <= datetime(?, '-5 seconds')
                )
            ''', (current_time.isoformat(),))
            
            # 更新最近5秒内有更新且状态为stopped的服务器状态为running
            c.execute('''
                UPDATE servers
                SET status = 'running'
                WHERE id IN (
                    SELECT id FROM servers 
                    WHERE status = 'stopped'
                    AND status != 'maintenance'
                    AND datetime(last_update) >= datetime(?, '-5 seconds')
                )
            ''', (current_time.isoformat(),))
            
            conn.commit()
        finally:
            conn.close()

    def delete_server(self, server_id: str) -> bool:
        """删除指定服务器的所有记录"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
            c.execute('DELETE FROM servers WHERE id = ?', (server_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting server: {e}")
            return False
        finally:
            conn.close()

    def add_allowed_client(self, client_name: str):
        """添加允许的客户端"""
        conn = self.get_db()
        c = conn.cursor()
        try:
            c.execute('''
                INSERT INTO allowed_clients (name, created_at)
                VALUES (?, CURRENT_TIMESTAMP)
            ''', (client_name,))
            conn.commit()
        finally:
            conn.close()

    def is_client_allowed(self, client_name: str) -> bool:
        """检查客户端是否被允许"""
        conn = self.get_db()
        c = conn.cursor()
        try:
            c.execute('SELECT name FROM allowed_clients WHERE name = ?', (client_name,))
            return c.fetchone() is not None
        finally:
            conn.close()

    def delete_allowed_client(self, client_name: str):
        """删除允许的客户端"""
        conn = self.get_db()
        c = conn.cursor()
        try:
            # 删除允许的客户端
            c.execute('DELETE FROM allowed_clients WHERE name = ?', (client_name,))
            # 将相关服务器状态设置为stopped
            c.execute('''
                UPDATE servers 
                SET status = 'stopped' 
                WHERE name = ?
            ''', (client_name,))
            conn.commit()
        finally:
            conn.close()

    def set_admin_password(self, password: str) -> bool:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
            # 使用 bcrypt 进行密码加密
            password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            c.execute('INSERT OR REPLACE INTO admin_auth (password_hash, is_initialized) VALUES (?, TRUE)', 
                     (password_hash,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error setting password: {e}")
            return False
        finally:
            conn.close()

    def verify_password(self, password: str) -> bool:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
            c.execute('SELECT password_hash FROM admin_auth WHERE is_initialized = TRUE')
            result = c.fetchone()
            if not result:
                return False
            stored_hash = result[0]
            return bcrypt.checkpw(password.encode(), stored_hash)
        except Exception as e:
            print(f"Error verifying password: {e}")
            return False
        finally:
            conn.close()

    def is_initialized(self) -> bool:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
            c.execute('SELECT is_initialized FROM admin_auth WHERE is_initialized = TRUE')
            return bool(c.fetchone())
        finally:
            conn.close()
