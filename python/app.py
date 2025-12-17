from flask import Flask, render_template, jsonify, request
import os
import sqlite3
from bd import get_users, get_schedule, get_appointment, get_ScheduleTalon, check_doctor_login 
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


def send_talon_email(to_email, talon):
        """Отправляет электронный талон с деталями записи.
        talon — словарь с ключами: date, time, cabinet, doctor_name, patient_name
        """
        msg = EmailMessage()
        text = (f"Электронный талон\n\n"
                        f"Пациент: {talon.get('patient_name')}\n"
                        f"Врач: {talon.get('doctor_name')}\n"
                        f"Кабинет: {talon.get('cabinet')}\n"
                        f"Дата: {talon.get('date')}\n"
                        f"Время: {talon.get('time')}\n\n"
                        "Пожалуйста, приходите за 10 минут до приёма."
                     )
        html = f"""
        <html>
            <body>
                <h2>Электронный талон</h2>
                <p><strong>Пациент:</strong> {talon.get('patient_name')}</p>
                <p><strong>Врач:</strong> {talon.get('doctor_name')}</p>
                <p><strong>Кабинет:</strong> {talon.get('cabinet')}</p>
                <p><strong>Дата:</strong> {talon.get('date')}</p>
                <p><strong>Время:</strong> {talon.get('time')}</p>
                <p>Пожалуйста, приходите за 10 минут до приёма.</p>
            </body>
        </html>
        """
        msg.set_content(text)
        msg.add_alternative(html, subtype='html')
        msg['Subject'] = 'Электронный талон — Поликлиника'
        msg['From'] = 'policTRPO@gmail.com'
        msg['To'] = to_email
        try:
                with smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=20) as smtp:
                        smtp.login('policTRPO@gmail.com', 'aced ouzw kwph qisc')
                        smtp.send_message(msg)
        except Exception as e:
                print('Failed to send talon email:', e)
                return False
        return True

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
        try:
            cur.execute("SELECT sch.data_priema, sch.time_priema, d.name AS doctor_name, d.nom_cab AS cabinet "
                        "FROM schedule sch JOIN doctors d ON sch.id_doctor = d.id WHERE sch.id_rasp = ?", (slot_id,))
            row = cur.fetchone()
            if row:
                talon_info = {
                    'patient_name': info['fio'],
                    'doctor_name': row[2],
                    'cabinet': row[3],
                    'date': row[0],
                    'time': row[1]
                }
                send_talon_email(info['email'], talon_info)
        except Exception as e:
            print('Error preparing/sending talon email:', e)

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

app.secret_key = 'your_very_secret_key'

@app.route('/doctor', methods=['GET', 'POST'])
def doctor():
    if request.method == 'POST':
        doctor_id = request.form.get('doctor_id')
        password = request.form.get('password')
        
        with sqlite3.connect("polic.db") as con:
            doctor_user = check_doctor_login(con, doctor_id, password)
            
    return render_template('doctor.html')

if __name__ == '__main__':
    app.run(debug=True)



