import sqlite3
from datetime import datetime, timedelta


def generate_slots(date_str, work_time_str, doctor_id, interval_minutes=30):
    try:
        start_time_str, end_time_str = [t.strip() for t in work_time_str.split('-')]
    except ValueError:
        return []
        
    try:
        start_dt = datetime.strptime(f"{date_str} {start_time_str}", '%Y-%m-%d %H:%M')
        end_dt = datetime.strptime(f"{date_str} {end_time_str}", '%Y-%m-%d %H:%M')
    except ValueError:
        return []

    slots = []
    current_dt = start_dt

    while current_dt < end_dt:
        slot_time = current_dt.strftime('%H:%M')
        slots.append({
            'id_doctor': doctor_id,
            'data_priema': date_str,
            'time_priema': slot_time
        })
        current_dt += timedelta(minutes=interval_minutes)
    return slots


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
GENERATION_DATES = {
    '2025-11-19': 'wednesday',
    '2025-11-20': 'thursday'
}
APPOINTMENT_INTERVAL_MINUTES = 30


def init_db(con):
    cur = con.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")

    cur.execute("DROP TABLE IF EXISTS talon")
    cur.execute("DROP TABLE IF EXISTS med_card")
    cur.execute("DROP TABLE IF EXISTS pacient")
    cur.execute("DROP TABLE IF EXISTS schedule")
    cur.execute("DROP TABLE IF EXISTS work_schedule")
    cur.execute("DROP TABLE IF EXISTS doctors")
    cur.execute("DROP TABLE IF EXISTS specialize")

    cur.execute("""CREATE TABLE IF NOT EXISTS specialize (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE, opis TEXT)""")
    cur.execute("INSERT OR IGNORE INTO specialize VALUES(1,'Терапевт','Проводит первичную диагностику, назначает анализы и лечение.')")
    cur.execute("INSERT OR IGNORE INTO specialize VALUES(2,'Проктолог','Диагностика и лечение заболеваний толстой и прямой кишки.')")
    cur.execute("INSERT OR IGNORE INTO specialize VALUES(3,'Хирург','Оперативное лечение заболеваний и травм.')")
    cur.execute("INSERT OR IGNORE INTO specialize VALUES(4,'Гинеколог','Диагностика, лечение и профилактика заболеваний женской репродуктивной системы.')")

    cur.execute("""CREATE TABLE IF NOT EXISTS doctors (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, nom_cab INTEGER, work_time TEXT, id_spec INTEGER, photo TEXT, FOREIGN KEY (id_spec) REFERENCES specialize(id))""")
    cur.execute("INSERT OR IGNORE INTO doctors VALUES(1,'Волокитин Тимофей',201,'8.00-14.00',2, 'doctor1.jpg')")
    cur.execute("INSERT OR IGNORE INTO doctors VALUES(2,'Екатерина Мизулина',321,'14.00-20.00',1, 'doctor2.jpg')")
    cur.execute("INSERT OR IGNORE INTO doctors VALUES(3,'Акакий Харитонович',412,'8.00-14.00',3, 'doctor3.jpg')")
    cur.execute("INSERT OR IGNORE INTO doctors VALUES(4,'Азаркевич Никита',305,'10.00-16.00',4, 'doctor4.jpg')")
    cur.execute("INSERT OR IGNORE INTO doctors VALUES(5,'Мария Смирнова',214,'9.00-15.00',2, 'doctor5.jpg')")
    cur.execute("INSERT OR IGNORE INTO doctors VALUES(6,'Дмитрий Орлов',122,'12.00-18.00',3, 'doctor6.jpg')")
    cur.execute("INSERT OR IGNORE INTO doctors VALUES(7,'Наталья Петрова',301,'8.00-14.00',1, 'doctor7.jpg')")
    cur.execute("INSERT OR IGNORE INTO doctors VALUES(8,'Игорь Беляев',220,'13.00-19.00',2, 'doctor8.jpg')")

    cur.execute("""CREATE TABLE IF NOT EXISTS work_schedule (id_ws INTEGER PRIMARY KEY AUTOINCREMENT, id_doctor INTEGER NOT NULL UNIQUE, monday TEXT, tuesday TEXT, wednesday TEXT, thursday TEXT, friday TEXT, FOREIGN KEY (id_doctor) REFERENCES doctors(id))""")
    cur.executemany("""INSERT OR IGNORE INTO work_schedule (id_doctor, monday, tuesday, wednesday, thursday, friday) VALUES (?, ?, ?, ?, ?, ?)""", [item[0:] for item in WORK_SCHEDULE_DATA])

    cur.execute("""CREATE TABLE IF NOT EXISTS pacient (id_pac INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, nom INTEGER, id_card INTEGER)""")
    cur.execute("INSERT OR IGNORE INTO pacient VALUES(1,'Сергеев Альберт Альбертович',80295647812,1)")
    cur.execute("INSERT OR IGNORE INTO pacient VALUES(2,'Миско Александр Сергеевич',80297817399,2)")
    cur.execute("INSERT OR IGNORE INTO pacient VALUES(3,'Сватко Игорь Борисович',80291234354,3)")

    cur.execute("""CREATE TABLE IF NOT EXISTS med_card (id_card INTEGER PRIMARY KEY AUTOINCREMENT, id_pac INTEGER UNIQUE, spisok_zabol TEXT, FOREIGN KEY (id_pac) REFERENCES pacient(id_pac))""")
    cur.execute("INSERT OR IGNORE INTO med_card VALUES(1,1,'Грипп 20.03.2020, COVID-19 25.04.2021')")
    cur.execute("INSERT OR IGNORE INTO med_card VALUES(2,2,'Язва желудка 12.03.2023')")
    cur.execute("INSERT OR IGNORE INTO med_card VALUES(3,3,'Аппендицит 25.08.2025')")

    cur.execute("""CREATE TABLE IF NOT EXISTS schedule (
        id_rasp INTEGER PRIMARY KEY AUTOINCREMENT,
        id_doctor INTEGER NOT NULL,
        data_priema TEXT NOT NULL,
        time_priema TEXT NOT NULL,
        FOREIGN KEY (id_doctor) REFERENCES doctors(id)
    )""")
    
    cur.execute("""CREATE TABLE IF NOT EXISTS talon (
        id_talon INTEGER PRIMARY KEY AUTOINCREMENT,
        id_pac INTEGER NOT NULL,
        id_slot INTEGER NOT NULL UNIQUE,
        status TEXT CHECK(status IN ('Активный','Неактивный','Пройден')) DEFAULT 'Активный',
        FOREIGN KEY (id_pac) REFERENCES pacient(id_pac),
        FOREIGN KEY (id_slot) REFERENCES schedule(id_rasp)
    )""")

    all_slots = []
    
    for data in WORK_SCHEDULE_DATA:
        doc_id = data[0]
        
        schedule_map = {
            date: data[i+1]
            for date, day_name in GENERATION_DATES.items()
            for i, d in enumerate(['monday', 'tuesday', 'wednesday', 'thursday', 'friday'])
            if day_name == d
        }
        
        for date, work_time in schedule_map.items():
            if work_time and work_time.strip():
                slots = generate_slots(date, work_time, doc_id, APPOINTMENT_INTERVAL_MINUTES)
                all_slots.extend(slots)
                
    if all_slots:
        slot_insert_values = [(s['id_doctor'], s['data_priema'], s['time_priema']) for s in all_slots]
        cur.executemany("""
            INSERT INTO schedule (id_doctor, data_priema, time_priema) 
            VALUES (?, ?, ?)
        """, slot_insert_values)

    booked_slots = cur.execute("""
        SELECT id_rasp FROM schedule 
        LIMIT 3
    """).fetchall()

    con.commit()
    print("База данных 'polic.db' успешно инициализирована.")


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


if __name__ == '__main__':
        with sqlite3.connect("polic.db") as con:
            init_db(con)