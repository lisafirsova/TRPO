import sqlite3
from datetime import datetime, timedelta
import re
import os
import bcrypt
import logging 


APPOINTMENT_INTERVAL_MINUTES = 30
SLOTS_DAYS_AHEAD = 14
SLOTS_KEEP_DAYS = 30

def normalize_time_part(t: str) -> str:
    t = t.strip()
    t = t.replace('.', ':')
    if ':' not in t:
        t = f"{int(t):02d}:00"
    else:
        parts = t.split(':')
        h = int(parts[0]) if parts[0] else 0
        m = int(parts[1]) if len(parts) > 1 and parts[1] else 0
        t = f"{h:02d}:{m:02d}"
    return t

def parse_work_time(work_time_str: str):
    if not work_time_str or not work_time_str.strip():
        return None
    parts = re.split(r'[-–—]', work_time_str)
    if len(parts) < 2:
        parts = work_time_str.split()
        if len(parts) < 2:
            return None
    start_raw = parts[0].strip()
    end_raw = parts[1].strip()
    try:
        return normalize_time_part(start_raw), normalize_time_part(end_raw)
    except:
        return None

def generate_slots(date_str, work_time_str, doctor_id, interval_minutes=30):
    parsed = parse_work_time(work_time_str)
    if not parsed:
        return []
    start_time_str, end_time_str = parsed
    try:
        start_dt = datetime.strptime(f"{date_str} {start_time_str}", '%Y-%m-%d %H:%M')
        end_dt = datetime.strptime(f"{date_str} {end_time_str}", '%Y-%m-%d %H:%M')
    except ValueError:
        return []
    if end_dt <= start_dt:
        end_dt += timedelta(days=1)
    slots = []
    current_dt = start_dt
    while current_dt < end_dt:
        slot_time = current_dt.strftime('%H:%M')
        slots.append({'id_doctor': doctor_id, 'data_priema': date_str, 'time_priema': slot_time})
        current_dt += timedelta(minutes=interval_minutes)
    return slots

logger = logging.getLogger(__name__)

def hash_password(password):
    try:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    except Exception as e:
        logger.error(f"Ошибка при хешировании пароля: {e}")
        raise


WORK_SCHEDULE_DATA = [
    (1, '13:00 - 21:00', '13:00 - 21:00', '07:00 - 13:00', '07:00 - 13:00', '07:00 - 13:00'),
    (2, '7:00 - 13:00', '7:00 - 13:00', '13:00 - 21:00', '13:00 - 21:00', '13:00 - 21:00'),
    (3, '13:00 - 21:00', '13:00 - 21:00', '07:00 - 13:00', '07:00 - 13:00', '07:00 - 13:00'),
    (4, '7:00 - 13:00', '7:00 - 13:00', '13:00 - 21:00', '13:00 - 21:00', '13:00 - 21:00'),
    (5, '13:00 - 21:00', '13:00 - 21:00', '07:00 - 13:00', '07:00 - 13:00', '07:00 - 13:00'),
    (6, '7:00 - 13:00', '7:00 - 13:00', '13:00 - 21:00', '13:00 - 21:00', '13:00 - 21:00'),
    (7, '13:00 - 21:00', '13:00 - 21:00', '07:00 - 13:00', '07:00 - 13:00', '07:00 - 13:00'),
    (8, '7:00 - 13:00', '7:00 - 13:00', '13:00 - 21:00', '13:00 - 21:00', '13:00 - 21:00')
]

def init_db(con: sqlite3.Connection):
    cur = con.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")
    cur.execute("DROP TABLE IF EXISTS talon")
    cur.execute("DROP TABLE IF EXISTS med_card")
    cur.execute("DROP TABLE IF EXISTS pacient")
    cur.execute("DROP TABLE IF EXISTS schedule")
    cur.execute("DROP TABLE IF EXISTS work_schedule")
    cur.execute("DROP TABLE IF EXISTS doctors")
    cur.execute("DROP TABLE IF EXISTS specialize")

    cur.execute("""CREATE TABLE IF NOT EXISTS specialize (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    opis TEXT)""")
    cur.execute("INSERT OR IGNORE INTO specialize VALUES(1,'Терапевт','Проводит первичную диагностику, назначает анализы и лечение.')")
    cur.execute("INSERT OR IGNORE INTO specialize VALUES(2,'Проктолог','Диагностика и лечение заболеваний толстой и прямой кишки.')")
    cur.execute("INSERT OR IGNORE INTO specialize VALUES(3,'Хирург','Оперативное лечение заболеваний и травм.')")
    cur.execute("INSERT OR IGNORE INTO specialize VALUES(4,'Гинеколог','Диагностика, лечение и профилактика заболеваний женской репродуктивной системы.')")

    cur.execute("""CREATE TABLE IF NOT EXISTS doctors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    nom_cab INTEGER,
                    id_spec INTEGER,
                    photo TEXT,
                    password TEXT,
                    FOREIGN KEY (id_spec) REFERENCES specialize(id)
                )""")
    pas=[hash_password('1ВТ'),hash_password('2ЕМ'),hash_password('3АХ'),hash_password('4АН'),hash_password('5МС'),hash_password('6ДО'),hash_password('7НП'),hash_password('8ИБ')]
    cur.execute("INSERT OR IGNORE INTO doctors VALUES(?,?,?,?,?,?)",(1,'Волокитин Тимофей',201,2, 'doctor1.jpg',pas[0]))
    cur.execute("INSERT OR IGNORE INTO doctors VALUES(?,?,?,?,?,?)",(2,'Екатерина Мизулина',321,1, 'doctor2.jpg',pas[1]))
    cur.execute("INSERT OR IGNORE INTO doctors VALUES(?,?,?,?,?,?)",(3,'Акакий Харитонович',412,3, 'doctor3.jpg',pas[2]))
    cur.execute("INSERT OR IGNORE INTO doctors VALUES(?,?,?,?,?,?)",(4,'Азаркевич Никита',305,4, 'doctor4.jpg',pas[3]))
    cur.execute("INSERT OR IGNORE INTO doctors VALUES(?,?,?,?,?,?)",(5,'Мария Смирнова',214,2, 'doctor5.jpg',pas[4]))
    cur.execute("INSERT OR IGNORE INTO doctors VALUES(?,?,?,?,?,?)",(6,'Дмитрий Орлов',122,3, 'doctor6.jpg',pas[5]))
    cur.execute("INSERT OR IGNORE INTO doctors VALUES(?,?,?,?,?,?)",(7,'Наталья Петрова',301,1, 'doctor7.jpg',pas[6]))
    cur.execute("INSERT OR IGNORE INTO doctors VALUES(?,?,?,?,?,?)",(8,'Игорь Беляев',220,2, 'doctor8.jpg',pas[7]))
 

    cur.execute("""CREATE TABLE IF NOT EXISTS work_schedule (
                    id_ws INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_doctor INTEGER NOT NULL UNIQUE,
                    monday TEXT, tuesday TEXT, wednesday TEXT, thursday TEXT, friday TEXT,
                    FOREIGN KEY (id_doctor) REFERENCES doctors(id)
                )""")
    cur.executemany("""INSERT OR IGNORE INTO work_schedule (id_doctor, monday, tuesday, wednesday, thursday, friday)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    [item[0:] for item in WORK_SCHEDULE_DATA])

    cur.execute("""CREATE TABLE IF NOT EXISTS pacient (
                    id_pac INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    nom INTEGER)""")

    cur.execute("""CREATE TABLE IF NOT EXISTS schedule (
                    id_rasp INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_doctor INTEGER NOT NULL,
                    data_priema TEXT NOT NULL,
                    time_priema TEXT NOT NULL,
                    FOREIGN KEY (id_doctor) REFERENCES doctors(id)
                )""")
    cur.execute("""CREATE UNIQUE INDEX IF NOT EXISTS idx_schedule_unique
                   ON schedule(id_doctor, data_priema, time_priema)""")

    cur.execute("""CREATE TABLE IF NOT EXISTS talon (
                    id_talon INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_pac INTEGER NOT NULL,
                    id_slot INTEGER NOT NULL UNIQUE,
                    status TEXT CHECK(status IN ('Активный','Неактивный','Пройден')) DEFAULT 'Активный',
                    FOREIGN KEY (id_pac) REFERENCES pacient(id_pac),
                    FOREIGN KEY (id_slot) REFERENCES schedule(id_rasp)
                )""")

    all_slots = []
    today = datetime.now().date()
    for data in WORK_SCHEDULE_DATA:
        doc_id = data[0]
        work_times = data[1:]
        for delta in range(SLOTS_DAYS_AHEAD):
            date_obj = today + timedelta(days=delta)
            weekday_index = date_obj.weekday()
            if weekday_index > 4:
                continue
            work_time = work_times[weekday_index] if weekday_index < len(work_times) else None
            if work_time and work_time.strip():
                date_str = date_obj.strftime('%Y-%m-%d')
                slots = generate_slots(date_str, work_time, doc_id, APPOINTMENT_INTERVAL_MINUTES)
                all_slots.extend(slots)

    if all_slots:
        slot_insert_values = [(s['id_doctor'], s['data_priema'], s['time_priema']) for s in all_slots]
        cur.executemany("""
            INSERT OR IGNORE INTO schedule (id_doctor, data_priema, time_priema)
            VALUES (?, ?, ?)
        """, slot_insert_values)

    con.commit()
    cleanup_old_slots(con, days_to_keep=SLOTS_KEEP_DAYS)

def cleanup_old_slots(con: sqlite3.Connection, days_to_keep: int = 30):
    cur = con.cursor()
    today_str = datetime.now().date().strftime('%Y-%m-%d')
    cutoff_date = (datetime.now().date() - timedelta(days=days_to_keep)).strftime('%Y-%m-%d')
    cur.execute("""
        UPDATE talon
        SET status = 'Пройден'
        WHERE id_slot IN (
            SELECT id_rasp FROM schedule WHERE data_priema < ?
        ) AND status != 'Пройден'
    """, (today_str,))
    cur.execute("""
        DELETE FROM talon
        WHERE id_slot IN (
            SELECT id_rasp FROM schedule WHERE data_priema < ?
        )
    """, (cutoff_date,))
    cur.execute("""
        DELETE FROM schedule
        WHERE data_priema < ?
    """, (cutoff_date,))
    con.commit()

def get_users(con):
    con.row_factory = sqlite3.Row
    cursor = con.cursor()
    cursor.execute("""
        SELECT d.name AS doctor_name,
               d.photo AS doctor_photo,
               s.name AS spec_name
        FROM doctors d
        JOIN specialize s ON d.id_spec = s.id
    """)
    return cursor.fetchall()

def get_schedule(con):
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
        ORDER BY s.name, d.nom_cab
    """)
    return cur.fetchall()

def get_appointment(con):
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("""
        SELECT 
            d.id AS doctor_id,
            d.name AS doctor_name,
            s.name AS spec_name
        FROM doctors d
        JOIN specialize s ON d.id_spec = s.id
    """)
    data = [dict(row) for row in cur.fetchall()]
    doctors_data = [{"doctor_id": row["doctor_id"], "doctor_name": row["doctor_name"], "spec_name": row["spec_name"]} for row in data]
    specialties = sorted(list({row['spec_name'] for row in data}))
    return doctors_data, specialties

def get_ScheduleTalon(con, doctor_id):
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("""
        SELECT
            sch.id_rasp,
            sch.data_priema,
            sch.time_priema,
            CASE
                WHEN t.id_talon IS NULL THEN 'свободен'
                WHEN t.status = 'Активный' THEN 'занят'
                ELSE 'занят'
            END AS status_slot,
            t.id_talon,
            t.status AS booking_status,
            p.name AS pacient_name
        FROM 
            schedule sch
        LEFT JOIN 
            talon t ON sch.id_rasp = t.id_slot
        LEFT JOIN
            pacient p ON t.id_pac = p.id_pac 
        WHERE 
            sch.id_doctor = ?
        ORDER BY sch.data_priema, sch.time_priema;
    """, (doctor_id,))
    return [dict(row) for row in cur.fetchall()]

def check_doctor_login(con, name_input, plain_password):
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT id, name, password FROM doctors WHERE name = ?", (name_input,))
    user = cur.fetchone()
    if user:
        stored_hash = user['password']
        if bcrypt.checkpw(plain_password.encode('utf-8'), stored_hash.encode('utf-8')):
            return user
    return None

def book_slot(con: sqlite3.Connection, id_pac: int, id_rasp: int):
    cur = con.cursor()
    cur.execute("SELECT id_rasp FROM schedule WHERE id_rasp = ?", (id_rasp,))
    row = cur.fetchone()
    if not row:
        return False, "Слот не найден."
    cur.execute("SELECT id_talon, status FROM talon WHERE id_slot = ?", (id_rasp,))
    existing = cur.fetchone()
    if existing:
        return False, "Слот уже занят."
    try:
        cur.execute("INSERT INTO talon (id_pac, id_slot, status) VALUES (?, ?, 'Активный')", (id_pac, id_rasp))
        con.commit()
        return True, "Талон успешно создан."
    except sqlite3.IntegrityError as e:
        return False, f"Ошибка при создании талона: {e}"

def mark_past_talons_as_passed(con: sqlite3.Connection):
    cur = con.cursor()
    today_str = datetime.now().date().strftime('%Y-%m-%d')
    cur.execute("""
        UPDATE talon
        SET status = 'Пройден'
        WHERE id_slot IN (
            SELECT id_rasp FROM schedule WHERE data_priema < ?
        ) AND status != 'Пройден'
    """, (today_str,))
    con.commit()

def get_doctor_patients(con, doctor_id):
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("""
        SELECT 
            sch.data_priema AS date, 
            sch.time_priema AS time, 
            p.name AS patient_name, 
            p.nom AS phone
        FROM schedule sch
        JOIN talon t ON sch.id_rasp = t.id_slot
        JOIN pacient p ON t.id_pac = p.id_pac
        WHERE sch.id_doctor = ?
        ORDER BY sch.data_priema ASC, sch.time_priema ASC
    """, (doctor_id,))
    return [dict(row) for row in cur.fetchall()]


if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, "polic.db")
    
    with sqlite3.connect(db_path) as con:
        init_db(con)
