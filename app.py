from flask import Flask, render_template, request
import sqlite3
import os

app = Flask(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), "dance.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def get_dancer_list():
    """Get all distinct dancer names"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT name FROM competitions ORDER BY name ASC")
    names = [row[0] for row in cur.fetchall()]
    conn.close()
    return names

def get_level_list():
    """Get all distinct levels"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT level FROM competitions ORDER BY level ASC")
    levels = [row[0] for row in cur.fetchall()]
    conn.close()
    return levels

def get_dancer_data(name=None, level=None):
    """Retrieve detailed competition data"""
    conn = get_connection()
    cur = conn.cursor()
    query = "SELECT * FROM competitions WHERE 1=1"
    params = []
    if name:
        query += " AND name = ?"
        params.append(name)
    if level:
        query += " AND level = ?"
        params.append(level)
    cur.execute(query, params)
    data = cur.fetchall()
    conn.close()
    return data

def get_summary_data(name=None, level=None):
    """Retrieve summary (totals per dancer)"""
    conn = get_connection()
    cur = conn.cursor()
    query = """
        SELECT name, SUM(points) AS total_points, MAX(level) AS current_level
        FROM competitions
        WHERE 1=1
    """
    params = []
    if name:
        query += " AND name = ?"
        params.append(name)
    if level:
        query += " AND level = ?"
        params.append(level)
    query += " GROUP BY name ORDER BY total_points DESC"
    cur.execute(query, params)
    data = cur.fetchall()
    conn.close()
    return data

@app.route('/', methods=['GET', 'POST'])
def index():
    name = request.form.get('name')
    level = request.form.get('level')
    dancers = get_dancer_data(name, level)
    dancer_list = get_dancer_list()
    level_list = get_level_list()
    return render_template('competitions.html', dancers=dancers, dancer_list=dancer_list, level_list=level_list)

@app.route('/summary', methods=['GET', 'POST'])
def summary():
    name = request.form.get('name')
    level = request.form.get('level')
    summary_data = get_summary_data(name, level)
    dancer_list = get_dancer_list()
    level_list = get_level_list()
    return render_template('summary.html', summary=summary_data, dancer_list=dancer_list, level_list=level_list)

if __name__ == '__main__':
    app.run(debug=True)