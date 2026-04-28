import os
import json
import psycopg2
from flask import Flask

app = Flask(__name__)

def get_config():
    config_path = '/etc/mywebapp/config.json'
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    return {
        "port": 3000,
        "db_host": "127.0.0.1",
        "db_name": "inventory",
        "db_user": "app",
        "db_password": "password"
    }

@app.route('/', methods=['GET'])
def index():
    return """
    <ul>
        <li><a href="/items">GET /items</a></li>
        <li><a href="/health/alive">GET /health/alive</a></li>
        <li><a href="/health/ready">GET /health/ready</a></li>
    </ul>
    """, 200, {'Content-Type': 'text/html'}

@app.route('/health/alive', methods=['GET'])
def alive():
    return "OK", 200

@app.route('/health/ready', methods=['GET'])
def ready():
    cfg = get_config()
    try:
        conn = psycopg2.connect(
            host=cfg['db_host'],
            database=cfg['db_name'],
            user=cfg['db_user'],
            password=cfg['db_password']
        )
        conn.close()
        return "OK", 200
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    cfg = get_config()
    app.run(host='0.0.0.0', port=cfg.get('port', 3000))