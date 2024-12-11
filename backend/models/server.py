from datetime import datetime
import sqlite3
from typing import Dict, List
import bcrypt
import hashlib
import os
import jwt
from config import Config
import logging

class Server:
    # Add status constants
    STATUS_RUNNING = 'running'
    STATUS_STOPPED = 'stopped'
    STATUS_MAINTENANCE = 'maintenance'
    
    # Add timeout configuration
    CONNECTION_TIMEOUT = 30  # Connection timeout in seconds
    
    def __init__(self, db_path: str):
        self.db_path = db_path

    def init_db(self):
        """Initialize database and create required tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Ensure the database directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        try:
            # Create tables (if not exists)
            c.execute('''
                CREATE TABLE IF NOT EXISTS servers (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    type TEXT,
                    location TEXT,
                    ip_address TEXT,
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
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_connected INTEGER DEFAULT 0
                )
            ''')
            
            # Add index for performance
            c.execute('''
                CREATE INDEX IF NOT EXISTS idx_client_name 
                ON allowed_clients(name)
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
            print("Database initialized successfully")
        except Exception as e:
            print(f"Error initializing database: {e}")
            raise
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
            # Get current status
            c.execute('SELECT status FROM servers WHERE name = ?', (server_data['name'],))
            current = c.fetchone()
            old_status = current[0] if current else 'unknown'
            
            # Modify status logic
            # If client update is received, the server is considered running
            server_data['status'] = 'running'
            
            # Update timestamp
            server_data['last_update'] = datetime.now().isoformat()
            
            # Log status change
            if old_status != server_data['status']:
                self.log_status_change(server_data['name'], old_status, server_data['status'])
            
            # Execute update
            c.execute('''
                UPDATE servers 
                SET type = ?,
                    location = ?,
                    ip_address = ?,
                    status = ?,
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
                    last_update = ?
                WHERE name = ?
            ''', (
                server_data.get('type', 'Unknown'),
                server_data.get('location', 'UN'),
                server_data.get('ip_address', '127.0.0.1'),
                server_data['status'],
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
                server_data['last_update'],
                server_data['name']
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
        """Unified server status check method"""
        conn = self.get_db()
        c = conn.cursor()
        try:
            current_time = datetime.now()
            
            # Get all servers that need to be checked
            c.execute('''
                SELECT id, name, last_update, status
                FROM servers 
                WHERE status = 'running'
                AND datetime(last_update) < datetime(?, '-30 seconds')
                AND status != 'maintenance'
            ''', (current_time.isoformat(),))
            
            servers_to_check = c.fetchall()
            
            for server_id, name, last_update, status in servers_to_check:
                last_update_time = datetime.fromisoformat(last_update)
                if (current_time - last_update_time).total_seconds() > 30:
                    c.execute('''
                        UPDATE servers
                        SET status = 'stopped'
                        WHERE id = ? AND status = 'running'
                    ''', (server_id,))
                    self.log_status_change(name, 'running', 'stopped')
            
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
                 cpu, memory, disk, os_type, order_index, last_update, cpu_info, 
                 total_memory, total_disk, ip_address)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?, ?, ?, ?)
            ''', (
                server_id,
                client_name,
                'VPS',
                'Pending',
                'maintenance',
                1,
                1024,
                1024,
                0,
                0,
                0,
                'Linux',
                0,
                'N/A',
                0,
                0,
                'N/A'
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

    def verify_token(self, token: str) -> bool:
        """Verify JWT token"""
        try:
            jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
            return True
        except:
            return False

    def update_client_connection(self, client_name: str, is_connected: bool):
        """Update client connection status"""
        conn = self.get_db()
        c = conn.cursor()
        try:
            c.execute('''
                UPDATE allowed_clients 
                SET is_connected = ? 
                WHERE name = ?
            ''', (1 if is_connected else 0, client_name))
            conn.commit()
        finally:
            conn.close()

    def update_last_activity(self, client_name: str):
        """Update client's last activity time"""
        conn = self.get_db()
        c = conn.cursor()
        try:
            current_time = datetime.now().isoformat()
            c.execute('''
                UPDATE servers 
                SET last_update = ?,
                    status = 'running'
                WHERE name = ?
            ''', (current_time, client_name))
            conn.commit()
        finally:
            conn.close()

    def check_client_connection(self, client_name: str):
        """Check client connection based on last activity"""
        conn = self.get_db()
        c = conn.cursor()
        try:
            c.execute('''
                SELECT last_update 
                FROM servers 
                WHERE name = ?
            ''', (client_name,))
            result = c.fetchone()
            
            if result:
                last_update = datetime.fromisoformat(result[0])
                current_time = datetime.now()
                
                # Change timeout from 20 seconds to 30 seconds to match check_server_status
                if (current_time - last_update).total_seconds() <= 30:
                    return
                
            # If no update within 30 seconds or no record found, set status to stopped
            c.execute('''
                UPDATE servers 
                SET status = 'stopped' 
                WHERE name = ? 
                AND status = 'running'
            ''', (client_name,))
            conn.commit()
        finally:
            conn.close()

    def log_status_change(self, server_name: str, old_status: str, new_status: str):
        """Enhanced status change logging"""
        current_time = datetime.now().isoformat()
        log_message = f"{current_time} - Server '{server_name}' status changed: {old_status} -> {new_status}"
        
        # Write to log file
        logging.info(log_message)