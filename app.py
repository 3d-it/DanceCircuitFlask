from flask import Flask, render_template, request
import sqlite3
import os
import random

app = Flask(__name__)

# Database filename (no absolute paths for Render)
DB_PATH = "dance.db"


# ----------------------------------------
# Database helpers
# ----------------------------------------
def get_connection():
    return sqlite3.connect(DB_PATH)


def get_dancer_data(name=None, level=None):
    conn = get_connection()
    cur = conn.cursor()
    query = "SELECT * FROM competitions WHERE 1=1"
    params = []
    if name:
        query += " AND name LIKE ?"
        params.append(f"%{name}%")
    if level:
        query += " AND level LIKE ?"
        params.append(f"%{level}%")
    cur.execute(query, params)
    data = cur.fetchall()
    conn.close()
    return data


def get_summary_data():
    conn = get_connection()
    cur = conn.cursor()
    query = """
    SELECT name, SUM(points) AS total_points, MAX(level) AS current_level
    FROM competitions
    GROUP BY name
    ORDER BY total_points DESC
    """
    cur.execute(query)
    data = cur.fetchall()
    conn.close()
    return data


# ----------------------------------------
# Routes
# ----------------------------------------
@app.route('/', methods=['GET', 'POST'])
def index():
    name = request.form.get('name')
    level = request.form.get('level')
    dancers = get_dancer_data(name, level)
    return render_template('competitions.html', dancers=dancers)


@app.route('/summary')
def summary():
    summary_data = get_summary_data()
    return render_template('summary.html', summary=summary_data)


@app.route('/resetdb')
def reset_db():
    """Clears and repopulates the database with fictitious data."""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Create tables
    cur.execute("""
    CREATE TABLE dancers (
        name TEXT PRIMARY KEY,
        current_level TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE competitions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        competition_name TEXT,
        level TEXT,
        points INTEGER,
        FOREIGN KEY (name) REFERENCES dancers (name)
    )
    """)

    # Fictional dancer data
    dancers = [
        ("Luna Greystone", "Novice"), ("Elias Thorne", "Intermediate"),
        ("Maris Alder", "Newcomer"), ("Rowan Vale", "Advanced"),
        ("Ivy Renard", "Advanced"), ("Kieran Frost", "Intermediate"),
        ("Sable Wynn", "Novice"), ("Alaric Dune", "Newcomer"),
        ("Vera Solen", "Intermediate"), ("Finn Oren", "Novice"),
        ("Cassia Vale", "Advanced"), ("Ronan Pike", "Newcomer"),
        ("Thalia Reeve", "Intermediate"), ("Silas Merrin", "Novice"),
        ("Aurelia Knox", "Advanced"), ("Dax Halden", "Intermediate"),
        ("Seren Lyric", "Advanced"), ("Calder Voss", "Novice"),
        ("Nora Wren", "Newcomer"), ("Jalen Cross", "Intermediate"),
        ("Maeve Torrin", "Advanced"), ("Orin Faye", "Novice"),
        ("Lyra Morn", "Newcomer"), ("Bastian Rook", "Advanced"),
        ("Corin Elen", "Intermediate"), ("Tessa Wynn", "Novice"),
        ("Rhett Sol", "Intermediate"), ("Arden Vale", "Advanced"),
        ("Kael Brin", "Newcomer"), ("Eira Moss", "Novice"),
        ("Dorian Pike", "Intermediate"), ("Soren Vale", "Advanced"),
        ("Isla Venn", "Intermediate"), ("Nico Trask", "Newcomer"),
        ("Ember Talon", "Novice"), ("Mira Goss", "Intermediate"),
        ("Talon Vire", "Advanced"), ("Zara Crest", "Novice"),
        ("Lucan Hale", "Intermediate"), ("Renna Dusk", "Advanced")
    ]
    cur.executemany("INSERT INTO dancers (name, current_level) VALUES (?, ?)", dancers)

    # Fictional competitions
    comps = [
        "Amberlight Gala", "Crystal Echo Festival", "Moonveil Classic",
        "Velora Championship", "Ironbrook Invitational", "Halcyon Swing Bash",
        "Silverfall Open", "Ravenridge Cup", "Driftwood Pro Fest",
        "Aetherwave Challenge", "Lunaris Grand Prix", "Obsidian Step Classic",
        "Frostvale Invitational", "Emberreach Bash", "Aurora Bloom Showcase",
        "Stormcrest Cup", "Starspire Nationals", "Glacier Waltz Open",
        "Celestine Swing-Off", "Twilight Tempo Tournament", "Solvane Step Expo",
        "Radiant Dancer Fest", "Cinderpoint Pro Classic", "Whisperwind Open",
        "Crimson Trail Bash"
    ]
    levels = ["Newcomer", "Novice", "Intermediate", "Advanced", "Pro"]

    competitions = []
    for dancer in dancers:
        name = dancer[0]
        level = dancer[1]
        for _ in range(random.randint(3, 4)):
            comp_name = random.choice(comps)
            points = random.randint(15, 65)
            competitions.append((name, comp_name, level, points))

    cur.executemany("""
    INSERT INTO competitions (name, competition_name, level, points)
    VALUES (?, ?, ?, ?)
    """, competitions)

    conn.commit()
    conn.close()
    return f"<h3>✅ Database reset with {len(dancers)} dancers and {len(competitions)} competitions (all fictitious).</h3><a href='/'>Back to Home</a>"


# ----------------------------------------
# Auto-create database on startup
# ----------------------------------------
def init_db():
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS competitions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            competition_name TEXT,
            level TEXT,
            points INTEGER
        );
        """)
        conn.commit()
        conn.close()
        print("Database created automatically ✅")


init_db()


# ----------------------------------------
# Run the app
# ----------------------------------------
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
