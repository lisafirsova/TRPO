from flask import Flask, render_template, jsonify, request, redirect, url_for
import os
import sqlite3
from bd import get_users, get_schedule, get_appointment, get_ScheduleTalon, check_doctor_login, get_doctor_patients, hash_password, get_specialties, generate_slots
from email.message import EmailMessage
import smtplib
import random
import string


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(CURRENT_DIR, 'polic.db')

TEMPLATE_DIR = os.path.join(BASE_DIR, 'website')
STATIC_DIR = os.path.join(TEMPLATE_DIR, 'static')

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.secret_key = 'your_very_secret_key'

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
    msg = EmailMessage()
    text = (f"Электронный талон\n\n"
            f"Пациент: {talon.get('patient_name')}\n"
            f"Врач: {talon.get('doctor_name')}\n"
            f"Кабинет: {talon.get('cabinet')}\n"
            f"Дата: {talon.get('date')}\n"
            f"Время: {talon.get('time')}\n\n"
            "Пожалуйста, приходите за 10 минут до приёма.")
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
    
    with sqlite3.connect(DB_PATH) as con:
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
    with sqlite3.connect(DB_PATH) as con:
        doctors = get_users(con)
    return render_template('structure.html', doctors=doctors)

@app.route('/schedule')
def schedule():
    with sqlite3.connect(DB_PATH) as con:
        schedule_data = get_schedule(con)
    return render_template('schedule.html', schedule_data=schedule_data)

@app.route('/appointment')
def appointment():
    with sqlite3.connect(DB_PATH) as con:
        doctors_data, specialties = get_appointment(con)
    return render_template('appointment.html', doctors_data=doctors_data, specialties=specialties)

@app.route('/api/schedule/<int:doctor_id>', methods=['GET'])
def api_get_schedule(doctor_id):
    with sqlite3.connect(DB_PATH) as con:
        schedule_slots = get_ScheduleTalon(con, doctor_id)
    return jsonify(schedule_slots)


@app.route('/api/schedule', methods=['GET'])
def api_get_schedule_by_spec():
    specialty = request.args.get('specialty')
    if not specialty:
        return jsonify([])

    with sqlite3.connect(DB_PATH) as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("""
            SELECT 
                sch.id_rasp, 
                sch.data_priema, 
                sch.time_priema, 
                d.name AS doctor_name,
                CASE 
                    WHEN t.id_talon IS NULL THEN 'свободен' 
                    ELSE 'занят' 
                END AS status_slot
            FROM schedule sch
            JOIN doctors d ON sch.id_doctor = d.id
            JOIN specialize s ON d.id_spec = s.id
            LEFT JOIN talon t ON sch.id_rasp = t.id_slot
            WHERE s.name = ? 
              AND (t.id_talon IS NULL OR t.status != 'Активный')
            ORDER BY sch.data_priema, sch.time_priema
        """, (specialty,))
        
        slots = [dict(row) for row in cur.fetchall()]
    return jsonify(slots)

def is_admin(doctor_id, password):
    return str(doctor_id) == "AdminAdmin" and password == "Admin_QaZwsX911"

@app.route('/doctor', methods=['GET', 'POST'])
def doctor():
    if request.method == 'POST':
        doctor_name = request.form.get('doctor_id')
        password = request.form.get('password')
        if not doctor_name or not password:
            return render_template('doctor.html', error='Введите ID и пароль')
        if is_admin(doctor_name, password):
            return admin_panel()
        
        with sqlite3.connect(DB_PATH) as con:
            doctor_user = check_doctor_login(con, doctor_name, password)
            if doctor_user:
                patients_data = get_doctor_patients(con, doctor_user['id'])
                return render_template('tableForDoctor.html', 
                                     talons=patients_data, 
                                     doctor_name=doctor_user['name'])
            else:
                return render_template('doctor.html', error='Неверный логин или пароль')
    
    return render_template('doctor.html')

@app.route('/admin')
def admin_panel():
    error = request.args.get('error')
    success = request.args.get('success')
    
    with sqlite3.connect(DB_PATH) as con:
        con.row_factory = sqlite3.Row
        doctors = get_users(con)
        specialties = get_specialties(con)
        
        cur = con.cursor()
        cur.execute("""
            SELECT t.id_talon, p.name AS patient_name, sch.data_priema, sch.time_priema, 
                   d.name AS doctor_name, d.id AS doctor_id
            FROM talon t
            JOIN pacient p ON t.id_pac = p.id_pac
            JOIN schedule sch ON t.id_slot = sch.id_rasp
            JOIN doctors d ON sch.id_doctor = d.id
            WHERE t.status = 'Активный'
        """)
        talons = [dict(row) for row in cur.fetchall()]
        
    return render_template('admin.html', 
                         doctors=doctors, 
                         talons=talons, 
                         specialties=specialties,
                         error=error,
                         success=success) 

@app.route('/add-doctor', methods=['POST'])
def add_doctor():
    name = request.form.get('doctor-name')
    password = request.form.get('doctor-password')
    nom_cab = request.form.get('doctor-room')
    id_spec = request.form.get('doctor-specialty')

    if not all([name, password, nom_cab, id_spec]):
        return {"message": "Заполните все поля"}, 400

    hashed_password = hash_password(password)

    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.execute("INSERT INTO doctors (name, nom_cab, id_spec, password) VALUES (?, ?, ?, ?)",
                    (name, nom_cab, id_spec, hashed_password))
        con.commit()
    return {"message": "Врач успешно добавлен"}, 200

@app.route('/delete-appointment/<int:talon_id>', methods=['POST'])
def delete_appointment(talon_id):
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.execute("DELETE FROM talon WHERE id_talon = ?", (talon_id,))
        con.commit()
    return redirect(url_for('admin_panel'))
    

@app.route('/delete-doctor', methods=['POST'])
def delete_doctor():
    doctor_id = request.form.get('delete-doctor')
    if not doctor_id:
        return "Врач не выбран", 400

    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.execute("DELETE FROM schedule WHERE id_doctor = ?", (doctor_id,))
        cur.execute("DELETE FROM doctors WHERE id = ?", (doctor_id,))
        con.commit()
    return redirect(url_for('admin_panel'))

@app.route('/update-schedule', methods=['POST'])
def update_schedule():
    doc_id = request.form.get('schedule-doctor')
    date = request.form.get('schedule-date')
    time_start = request.form.get('schedule-time-start')
    time_end = request.form.get('schedule-time-end')

    if not all([doc_id, date, time_start, time_end]):
        return redirect(url_for('admin_panel', error='Заполните все поля'))

    try:
        from datetime import datetime
        schedule_date = datetime.strptime(date, '%Y-%m-%d')
        weekday = schedule_date.weekday()

        if weekday > 4:
            return redirect(url_for('admin_panel', error='Можно изменять расписание только на рабочие дни (пн-пт)'))
        start_dt = datetime.strptime(time_start, '%H:%M')
        end_dt = datetime.strptime(time_end, '%H:%M')
        
        if end_dt <= start_dt:
            return redirect(url_for('admin_panel', error='Время окончания должно быть позже времени начала'))
            
    except ValueError as e:
        return redirect(url_for('admin_panel', error=f'Неверный формат даты или времени: {str(e)}'))
    full_time = f"{time_start} - {time_end}"

    try:
        with sqlite3.connect(DB_PATH) as con:
            cur = con.cursor()
            
            cur.execute("SELECT id FROM doctors WHERE id = ?", (doc_id,))
            if not cur.fetchone():
                return redirect(url_for('admin_panel', error='Врач не найден'))
            weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
            weekday_column = weekdays[weekday]
            cur.execute("SELECT id_ws FROM work_schedule WHERE id_doctor = ?", (doc_id,))
            work_schedule_row = cur.fetchone()
            
            if work_schedule_row:
                cur.execute(f"""
                    UPDATE work_schedule 
                    SET {weekday_column} = ?
                    WHERE id_doctor = ?
                """, (full_time, doc_id))
                print(f"Обновлено work_schedule для врача {doc_id}, день: {weekday_column}")
            else:
                days_values = [None] * 5
                days_values[weekday] = full_time
                cur.execute("""
                    INSERT INTO work_schedule 
                    (id_doctor, monday, tuesday, wednesday, thursday, friday) 
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (doc_id, *days_values))
                print(f"Создана новая запись в work_schedule для врача {doc_id}")
            cur.execute("""
                DELETE FROM schedule 
                WHERE id_doctor = ? AND data_priema = ?
            """, (doc_id, date))
            slots = generate_slots(date, full_time, int(doc_id))
            if not slots:
                print(f"Не удалось создать слоты для {date} {full_time}")
                return redirect(url_for('admin_panel', 
                                     error='Не удалось создать слоты для указанного времени'))
            for slot in slots:
                cur.execute("""
                    INSERT INTO schedule (id_doctor, data_priema, time_priema) 
                    VALUES (?, ?, ?)
                """, (slot['id_doctor'], slot['data_priema'], slot['time_priema']))
            
            con.commit()
            print(f"Расписание обновлено для врача {doc_id} на {date} ({weekday_column}): {len(slots)} слотов")
            
        return redirect(url_for('admin_panel', 
                             success=f'Расписание успешно обновлено. Создано {len(slots)} слотов.'))
        
    except sqlite3.Error as e:
        print(f"Ошибка базы данных при обновлении расписания: {e}")
        return redirect(url_for('admin_panel', 
                             error=f'Ошибка базы данных: {str(e)}'))
    except Exception as e:
        print(f"Непредвиденная ошибка при обновлении расписания: {e}")
        return redirect(url_for('admin_panel', 
                             error=f'Ошибка: {str(e)}'))

if __name__ == '__main__':
    app.run(debug=True)