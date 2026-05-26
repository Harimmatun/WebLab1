import os
import json
import psycopg2

def get_config():
    config_path = '/etc/mywebapp/config.json'
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
            
    return {
        "db_host": os.environ.get('DB_HOST', '127.0.0.1'),
        "db_name": os.environ.get('DB_NAME', 'inventory'),
        "db_user": os.environ.get('DB_USER', 'mywebapp'),
        "db_password": os.environ.get('DB_PASSWORD', 'password')
    }

def migrate():
    cfg = get_config()
    conn = psycopg2.connect(
        host=cfg['db_host'],
        database=cfg['db_name'],
        user=cfg['db_user'],
        password=cfg['db_password']
    )
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            quantity INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    conn.close()
    print("Database migrated successfully!")

if __name__ == '__main__':
    migrate()