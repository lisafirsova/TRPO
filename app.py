from flask import Flask, render_template
import os
import sqlite3
from bd import get_users, get_schedule, get_appointment

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'website')
STATIC_DIR = os.path.join(TEMPLATE_DIR, 'static')
app = Flask(__name__, template_folder=TEMPLATE_DIR,static_folder=STATIC_DIR)

@app.route('/')
def index():
    doctors = get_users()
    return render_template('structure.html', doctors=doctors)

@app.route('/schedule')
def schedule():
    schedule_data = get_schedule()
    return render_template('schedule.html', schedule_data=schedule_data)

@app.route('/appointment')
def appointment():
    doctors_data, specialties = get_appointment()
    return render_template('appointment.html', doctors_data=doctors_data, specialties=specialties)

if __name__ == '__main__':
    app.run(debug=True)



