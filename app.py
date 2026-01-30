from flask import Flask, request, jsonify, render_template, send_from_directory
import sqlite3
import os

app = Flask(__name__, template_folder='templates')
DB_FILE = 'leave_system.db'

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS leaves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT NOT NULL,
            startDate TEXT NOT NULL,
            endDate TEXT NOT NULL,
            reason TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/leaves', methods=['GET'])
def get_leaves():
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM leaves').fetchall()
    conn.close()
    
    leaves = [dict(row) for row in rows]
    return jsonify(leaves)

@app.route('/api/leaves', methods=['POST'])
def add_leave():
    data = request.json
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO leaves (user, startDate, endDate, reason)
        VALUES (?, ?, ?, ?)
    ''', (data['user'], data['startDate'], data['endDate'], data['reason']))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

# 初始化数据库
init_db()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
