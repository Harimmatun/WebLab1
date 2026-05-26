import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, request, jsonify

app = Flask(__name__)

def get_config():
    config_path = '/etc/mywebapp/config.json'
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
            
    return {
        "port": int(os.environ.get('PORT', 3000)),
        "db_host": os.environ.get('DB_HOST', '127.0.0.1'),
        "db_name": os.environ.get('DB_NAME', 'inventory'),
        "db_user": os.environ.get('DB_USER', 'mywebapp'),
        "db_password": os.environ.get('DB_PASSWORD', 'password')
    }

def get_db():
    cfg = get_config()
    return psycopg2.connect(
        host=cfg['db_host'],
        database=cfg['db_name'],
        user=cfg['db_user'],
        password=cfg['db_password']
    )

@app.route('/', methods=['GET'])
def index():
    return """
    <ul>
        <li><a href="/items">GET /items</a> - Список усіх предметів</li>
        <li>POST /items - Створити новий предмет (JSON/Form)</li>
        <li>GET /items/&lt;id&gt; - Детальна інформація по запису</li>
    </ul>
    """, 200, {'Content-Type': 'text/html'}

@app.route('/health/alive', methods=['GET'])
def alive():
    return "OK", 200

@app.route('/health/ready', methods=['GET'])
def ready():
    try:
        conn = get_db()
        conn.close()
        return "OK", 200
    except Exception as e:
        return str(e), 500

@app.route('/items', methods=['GET', 'POST'])
def items():
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            name = data.get('name')
            quantity = data.get('quantity')
        else:
            name = request.form.get('name')
            quantity = request.form.get('quantity')
            
        cur.execute("INSERT INTO items (name, quantity) VALUES (%s, %s) RETURNING id", (name, quantity))
        new_id = cur.fetchone()['id']
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"id": new_id}), 201

    cur.execute("SELECT id, name FROM items")
    items_list = cur.fetchall()
    cur.close()
    conn.close()

    accept = request.headers.get('Accept', '')
    if 'text/html' in accept:
        html = "<table border='1'><tr><th>ID</th><th>Name</th></tr>"
        for item in items_list:
            html += f"<tr><td>{item['id']}</td><td>{item['name']}</td></tr>"
        html += "</table>"
        return html, 200, {'Content-Type': 'text/html'}
        
    return jsonify(items_list), 200

@app.route('/items/<int:item_id>', methods=['GET'])
def item_detail(item_id):
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, name, quantity, created_at FROM items WHERE id = %s", (item_id,))
    item = cur.fetchone()
    cur.close()
    conn.close()

    if not item:
        return "Not Found", 404

    accept = request.headers.get('Accept', '')
    if 'text/html' in accept:
        html = f"""
        <ul>
            <li>ID: {item['id']}</li>
            <li>Name: {item['name']}</li>
            <li>Quantity: {item['quantity']}</li>
            <li>Created At: {item['created_at']}</li>
        </ul>
        """
        return html, 200, {'Content-Type': 'text/html'}
        
    return jsonify(item), 200

if __name__ == '__main__':
    cfg = get_config()
    app.run(host='0.0.0.0', port=cfg.get('port', 3000))