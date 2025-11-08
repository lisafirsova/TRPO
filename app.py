from flask import Flask, render_template
import os
import sqlite3

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'website')
STATIC_DIR = os.path.join(TEMPLATE_DIR, 'static')
app = Flask(__name__, template_folder=TEMPLATE_DIR,static_folder=STATIC_DIR)

def get_users():
    with sqlite3.connect("polic.db") as con:
        con.row_factory = sqlite3.Row
        cursor = con.cursor()
        cursor.execute("""
        SELECT d.name, s.name AS spec_name
        FROM doctors d
        JOIN specialize s ON d.id_spec = s.id
    """)
        doctors = cursor.fetchall()
    return doctors

@app.route('/')
def index():
    doctors = get_users()
    return render_template('structure.html', doctors=doctors)

if __name__ == '__main__':
    app.run(debug=True)
