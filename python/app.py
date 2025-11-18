from flask import Flask, render_template, jsonify
import os
import sqlite3
from bd import get_users, get_schedule, get_appointment, get_ScheduleTalon

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'website')
STATIC_DIR = os.path.join(TEMPLATE_DIR, 'static')
app = Flask(__name__, template_folder=TEMPLATE_DIR,static_folder=STATIC_DIR)

@app.route('/')
def index():
    with sqlite3.connect("polic.db") as con:
        doctors = get_users(con)
    return render_template('structure.html', doctors=doctors)

@app.route('/schedule')
def schedule():
    with sqlite3.connect("polic.db") as con:
        schedule_data = get_schedule(con)
    return render_template('schedule.html', schedule_data=schedule_data)

@app.route('/appointment')
def appointment():
    with sqlite3.connect("polic.db") as con:
        doctors_data, specialties = get_appointment(con)
    return render_template('appointment.html', doctors_data=doctors_data, specialties=specialties)

@app.route('/api/schedule/<int:doctor_id>', methods=['GET'])
def api_get_schedule(doctor_id):
    with sqlite3.connect("polic.db") as con:
        schedule_slots = get_ScheduleTalon(con,doctor_id)
    return jsonify(schedule_slots)

if __name__ == '__main__':
    app.run(debug=True)



