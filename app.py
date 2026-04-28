import os
import json
from flask import Flask

app = Flask(__name__)

def get_config():
    config_path = '/etc/mywebapp/config.json'
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    return {"port": 3000}

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

if __name__ == '__main__':
    cfg = get_config()
    app.run(host='0.0.0.0', port=cfg.get('port', 3000))