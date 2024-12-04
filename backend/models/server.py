from datetime import datetime
import sqlite3
from typing import Dict, List
import bcrypt
import hashlib

class Server:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
            # Create table (if not exists)
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
                    cpu_info TEXT,
                    total_memory REAL,
                    total_disk REAL,
                    order_index INTEGER DEFAULT 0,
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Change all running servers to stopped
            c.execute('''
                UPDATE servers 
                SET status = 'stopped' 
                WHERE status = 'running'
            ''')
            
            # Create allowed clients table
            c.execute('''
                CREATE TABLE IF NOT EXISTS allowed_clients (
                    name TEXT PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create admin authentication table
            c.execute('''
                CREATE TABLE IF NOT EXISTS admin_auth (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    password_hash BLOB NOT NULL,
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
        conn = self.get_db()
        c = conn.cursor()
        try:
            # Check if it's an allowed client
            c.execute('SELECT name FROM allowed_clients WHERE name = ?', (server_data['name'],))
            if not c.fetchone():
                return False
            
            # Update server record
            c.execute('''
                UPDATE servers 
                SET type = ?,
                    location = ?,
                    status = 'running',
                    uptime = ?,
                    network_in = ?,
                    network_out = ?,
                    cpu = ?,
                    memory = ?,
                    disk = ?,
                    os_type = ?,
                    cpu_info = ?,
                    total_memory = ?,
                    total_disk = ?,
                    last_update = CURRENT_TIMESTAMP
                WHERE name = ?
            ''', (
                server_data.get('type', 'Unknown'),
                server_data.get('location', 'UN'),
                server_data.get('uptime', 0),
                server_data.get('network_in', 0),
                server_data.get('network_out', 0),
                server_data.get('cpu', 0),
                server_data.get('memory', 0),
                server_data.get('disk', 0),
                server_data.get('os_type', 'Unknown'),
                server_data.get('cpu_info', 'N/A'),
                server_data.get('total_memory', 0),
                server_data.get('total_disk', 0),
                server_data['name']
            ))
            conn.commit()
            return True
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
        """Check all server statuses and mark overdue servers as stopped"""
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
        """Check all server statuses and mark servers that haven't been updated for more than 5 seconds as stopped"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
            current_time = datetime.now()
            
            # Update servers that haven't been updated for more than 5 seconds and are in running status to stopped
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
            
            # Update servers that have been updated in the last 5 seconds and are in stopped status to running
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
        """Delete all records of the specified server"""
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
        """Add or update allowed clients and create initial server records"""
        if not client_name or not client_name.strip():
            raise Exception("Client name cannot be empty")
        
        client_name = client_name.strip()
        conn = self.get_db()
        c = conn.cursor()
        try:
            # Add ip_address column to the servers table if it doesn't exist
            c.execute('''
                ALTER TABLE servers ADD COLUMN ip_address TEXT;
            ''')
        except Exception:  # Changed from bare except to Exception
            pass  # Column might already exist
            
            # Delete existing client records (if any)
            c.execute('DELETE FROM allowed_clients WHERE name = ?', (client_name,))
            c.execute('DELETE FROM servers WHERE name = ?', (client_name,))
            
            # Add to the allowed clients list
            c.execute('''
                INSERT INTO allowed_clients (name, created_at)
                VALUES (?, CURRENT_TIMESTAMP)
            ''', (client_name,))
            
            # Create an initial server record with friendly default values
            server_id = hashlib.md5(client_name.encode('utf-8')).hexdigest()
            c.execute('''
                INSERT INTO servers 
                (id, name, type, location, status, uptime, network_in, network_out,
                 cpu, memory, disk, os_type, order_index, last_update, cpu_info, total_memory, total_disk)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?, ?, ?)
            ''', (
                server_id,
                client_name,
                'VPS',                # Server type
                'Pending',            # Location status
                'maintenance',        # Friendly status display
                1,                    # Uptime (1 day)
                1024,                 # Network_in (1KB/s)
                1024,                 # Network_out (1KB/s)
                0,                    # CPU (5%)
                0,                    # Memory (20%)
                0,                    # Disk (30%)
                'Linux',              # Operating system
                0,                    # Order index
                'N/A',               # CPU info
                0,                    # Total memory
                0,                    # Total disk
            ))
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise Exception(f"Failed to add client: {str(e)}")
        finally:
            conn.close()

    def is_client_allowed(self, client_name: str) -> bool:
        """Check if the client is allowed"""
        conn = self.get_db()
        c = conn.cursor()
        try:
            c.execute('SELECT name FROM allowed_clients WHERE name = ?', (client_name,))
            return c.fetchone() is not None
        finally:
            conn.close()

    def delete_allowed_client(self, client_name: str):
        """Delete allowed clients"""
        conn = self.get_db()
        c = conn.cursor()
        try:
            # Delete allowed clients
            c.execute('DELETE FROM allowed_clients WHERE name = ?', (client_name,))
            # Set related server status to stopped
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
            # Use bcrypt for password encryption
            password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            
            # Check if there is already a record
            c.execute('SELECT id FROM admin_auth LIMIT 1')
            result = c.fetchone()
            
            if result:
                # Update existing record
                c.execute('''
                    UPDATE admin_auth 
                    SET password_hash = ?, 
                        is_initialized = TRUE 
                    WHERE id = ?
                ''', (password_hash, result[0]))
            else:
                # Insert new record
                c.execute('''
                    INSERT INTO admin_auth 
                    (password_hash, is_initialized) 
                    VALUES (?, TRUE)
                ''', (password_hash,))
            
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