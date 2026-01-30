from flask import Flask, request, jsonify, render_template
import sqlite3
import os

app = Flask(__name__)
DB_FILE = 'leave_system.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # 创建请假表
    cursor.execute('''
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
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM leaves')
    rows = cursor.fetchall()
    conn.close()
    
    leaves = []
    for row in rows:
        leaves.append({
            'id': row[0],
            'user': row[1],
            'startDate': row[2],
            'endDate': row[3],
            'reason': row[4]
        })
    return jsonify(leaves)

@app.route('/api/leaves', methods=['POST'])
def add_leave():
    data = request.json
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO leaves (user, startDate, endDate, reason)
        VALUES (?, ?, ?, ?)
    ''', (data['user'], data['startDate'], data['endDate'], data['reason']))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    # 确保 templates 文件夹存在，Flask 默认在那里找 HTML
    if not os.path.exists('templates'):
        os.makedirs('templates')
    init_db()
    app.run(port=8000, debug=True)
