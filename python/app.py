from flask import Flask, render_template, jsonify, request
import os
import sqlite3
from bd import get_users, get_schedule, get_appointment, get_ScheduleTalon
from email.message import EmailMessage
import smtplib
import random
import string

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'website')
STATIC_DIR = os.path.join(TEMPLATE_DIR, 'static')
app = Flask(__name__, template_folder=TEMPLATE_DIR,static_folder=STATIC_DIR)
pending_confirmations = {}

def send_email(to_email, code):
    msg = EmailMessage()
    msg.set_content(f"Ваш код подтверждения: {code}")
    msg['Subject'] = 'Подтверждение записи в поликлинику'
    msg['From'] = 'policTRPO@gmail.com'
    msg['To'] = to_email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login('policTRPO@gmail.com', 'aced ouzw kwph qisc')
        smtp.send_message(msg)

@app.route('/api/book', methods=['POST'])
def api_book():
    data = request.get_json()
    slot_id = data.get('slot_id')
    fio = data.get('fio')
    dob = data.get('dob')
    phone = data.get('phone')
    email = data.get('email')

    if not all([slot_id, fio, dob, phone, email]):
        return {"message": "Заполните все поля"}, 400

    code = ''.join(random.choices(string.digits, k=6))
    pending_confirmations[slot_id] = {
        "fio": fio,
        "dob": dob,
        "phone": phone,
        "email": email,
        "code": code
    }

    try:
        send_email(email, code)
    except Exception as e:
        return {"message": f"Не удалось отправить email: {str(e)}"}, 500

    return {"message": "Код подтверждения отправлен на почту"}, 200

@app.route('/api/confirm', methods=['POST'])
def api_confirm():
    data = request.get_json()
    slot_id = data.get('slot_id')
    code_input = data.get('code')

    if slot_id not in pending_confirmations:
        return {"message": "Слот не найден или код истек"}, 400

    info = pending_confirmations[slot_id]
    if info['code'] != code_input:
        return {"message": "Неверный код"}, 400
    with sqlite3.connect("polic.db") as con:
        cur = con.cursor()
        cur.execute("INSERT INTO pacient (name, nom) VALUES (?, ?)", (info['fio'], info['phone']))
        patient_id = cur.lastrowid
        cur.execute("INSERT INTO talon (id_pac, id_slot, status) VALUES (?, ?, 'Активный')",
                    (patient_id, slot_id))
        con.commit()

    del pending_confirmations[slot_id]

    return {"message": "Запись подтверждена и сохранена"}, 200

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



