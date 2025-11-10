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
        SELECT d.name AS doctor_name,
        d.photo AS doctor_photo,
        s.name AS spec_name
        FROM doctors d
        JOIN specialize s ON d.id_spec = s.id
    """)
        doctors = cursor.fetchall()
    return doctors

def get_schedule():
    with sqlite3.connect("polic.db") as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("""
            SELECT 
                d.nom_cab AS cabinet,
                d.name AS doctor_name,
                s.name AS specialty,
                ws.monday, ws.tuesday, ws.wednesday, ws.thursday, ws.friday
            FROM doctors d
            JOIN specialize s ON d.id_spec = s.id
            LEFT JOIN work_schedule ws ON ws.id_doctor = d.id
            ORDER BY d.nom_cab
        """)
        data = cur.fetchall()
    return data

@app.route('/')
def index():
    doctors = get_users()[:3]
    return render_template('structure.html', doctors=doctors)

@app.route('/schedule')
def schedule():
    schedule_data = get_schedule()
    return render_template('schedule.html', schedule_data=schedule_data)



if __name__ == '__main__':
    app.run(debug=True)
