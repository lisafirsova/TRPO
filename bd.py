import sqlite3

with sqlite3.connect("polic.db") as con:
    cur = con.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")

#SPECIALIZE
    cur.execute("""CREATE TABLE IF NOT EXISTS specialize (id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,opis TEXT)""")
    cur.execute("INSERT OR IGNORE INTO specialize VALUES(1,'Терапевт','Проводит первичную диагностику, назначает анализы и лечение.')")
    cur.execute("INSERT OR IGNORE INTO specialize VALUES(2,'Проктолог','Диагностика и лечение заболеваний толстой и прямой кишки.')")
    cur.execute("INSERT OR IGNORE INTO specialize VALUES(3,'Хирург','Оперативное лечение заболеваний и травм.')")
    cur.execute("INSERT OR IGNORE INTO specialize VALUES(4,'Гинеколог','Диагностика, лечение и профилактика заболеваний женской репродуктивной системы.')")


#DOCTORS
    cur.execute("""CREATE TABLE IF NOT EXISTS doctors (id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,nom_cab INTEGER,work_time TEXT,id_spec INTEGER,photo TEXT, FOREIGN KEY (id_spec) REFERENCES specialize(id))""")
    cur.execute("INSERT OR IGNORE INTO doctors VALUES(1,'Волокитин Тимофей',201,'8.00-14.00',2, 'doctor1.jpg')")
    cur.execute("INSERT OR IGNORE INTO doctors VALUES(2,'Екатерина Мизулина',321,'14.00-20.00',1, 'doctor2.jpg')")
    cur.execute("INSERT OR IGNORE INTO doctors VALUES(3,'Акакий Харитонович',412,'8.00-14.00',3, 'doctor3.jpg')")
    cur.execute("INSERT OR IGNORE INTO doctors VALUES(4,'Азаркевич Никита',305,'10.00-16.00',4, 'doctor4.jpg')")
    cur.execute("INSERT OR IGNORE INTO doctors VALUES(5,'Мария Смирнова',214,'9.00-15.00',2, 'doctor5.jpg')")
    cur.execute("INSERT OR IGNORE INTO doctors VALUES(6,'Дмитрий Орлов',122,'12.00-18.00',3, 'doctor6.jpg')")
    cur.execute("INSERT OR IGNORE INTO doctors VALUES(7,'Наталья Петрова',301,'8.00-14.00',1, 'doctor7.jpg')")
    cur.execute("INSERT OR IGNORE INTO doctors VALUES(8,'Игорь Беляев',220,'13.00-19.00',2, 'doctor8.jpg')")
#WORK_SCHEDULE
    cur.execute("""CREATE TABLE IF NOT EXISTS work_schedule (id_ws INTEGER PRIMARY KEY AUTOINCREMENT,id_doctor INTEGER NOT NULL,monday TEXT,tuesday TEXT,wednesday TEXT,thursday TEXT,friday TEXT,FOREIGN KEY (id_doctor) REFERENCES doctors(id))""")
    cur.execute("""INSERT OR IGNORE INTO work_schedule (id_ws, id_doctor, monday, tuesday, wednesday, thursday, friday) VALUES 
                (1, 1, '13:00 - 21:00', '13:00 - 21:00', '07:00 - 13:00', '07:00 - 13:00', '07:00 - 13:00'),
                (2, 2, '7:00 - 13:00', '7:00 - 13:00', '13:00 - 21:00', '13:00 - 21:00', '13:00 - 21:00'),
                (3, 3, '13:00 - 21:00', '13:00 - 21:00', '07:00 - 13:00', '07:00 - 13:00', '07:00 - 13:00'),
                (4, 4, '7:00 - 13:00', '7:00 - 13:00', '13:00 - 21:00', '13:00 - 21:00', '13:00 - 21:00'),
                (5, 5, '13:00 - 21:00', '13:00 - 21:00', '07:00 - 13:00', '07:00 - 13:00', '07:00 - 13:00'),
                (6, 6, '7:00 - 13:00', '7:00 - 13:00', '13:00 - 21:00', '13:00 - 21:00', '13:00 - 21:00'),
                (7, 7, '13:00 - 21:00', '13:00 - 21:00', '07:00 - 13:00', '07:00 - 13:00', '07:00 - 13:00'),
                (8, 8, '7:00 - 13:00', '7:00 - 13:00', '13:00 - 21:00', '13:00 - 21:00', '13:00 - 21:00')
                """)

#PACIENT
    cur.execute("""CREATE TABLE IF NOT EXISTS pacient (id_pac INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, nom INTEGER, id_card INTEGER)""")
    cur.execute("INSERT OR IGNORE INTO pacient VALUES(1,'Сергеев Альберт Альбертович',80295647812,1)")
    cur.execute("INSERT OR IGNORE INTO pacient VALUES(2,'Миско Александр Сергеевич',80297817399,2)")
    cur.execute("INSERT OR IGNORE INTO pacient VALUES(3,'Сватко Игорь Борисович',80291234354,3)")

#MED_CARD
    cur.execute("""CREATE TABLE IF NOT EXISTS med_card (id_card INTEGER PRIMARY KEY AUTOINCREMENT,id_pac INTEGER,spisok_zabol TEXT,FOREIGN KEY (id_pac) REFERENCES pacient(id_pac))""")
    cur.execute("INSERT OR IGNORE INTO med_card VALUES(1,1,'Грипп 20.03.2020, COVID-19 25.04.2021')")
    cur.execute("INSERT OR IGNORE INTO med_card VALUES(2,2,'Язва желудка 12.03.2023')")
    cur.execute("INSERT OR IGNORE INTO med_card VALUES(3,3,'Аппендицит 25.08.2025')")

#TALON
    cur.execute("""CREATE TABLE IF NOT EXISTS talon (id_talon INTEGER PRIMARY KEY AUTOINCREMENT,id_pac INTEGER,id_doctor INTEGER,data_priema TEXT,time_priema TEXT,status TEXT, FOREIGN KEY (id_pac) REFERENCES pacient(id_pac),FOREIGN KEY (id_doctor) REFERENCES doctors(id))""")
    cur.execute("INSERT OR IGNORE INTO talon VALUES(1,1,2,'30.09.2025','13:10','Неактивный')")
    cur.execute("INSERT OR IGNORE INTO talon VALUES(2,2,1,'01.10.2025','15:00','Активный')")
    cur.execute("INSERT OR IGNORE INTO talon VALUES(3,3,3,'02.10.2025','09:00','Активный')")

#SCHEDULE
    cur.execute("""CREATE TABLE IF NOT EXISTS schedule (id_rasp INTEGER PRIMARY KEY AUTOINCREMENT,id_talon INTEGER,id_doctor INTEGER NOT NULL,data_priema TEXT NOT NULL,time_priema TEXT NOT NULL,status TEXT CHECK(status IN ('свободен','занят')) DEFAULT 'свободен', FOREIGN KEY (id_talon) REFERENCES talon(id_talon), FOREIGN KEY (id_doctor) REFERENCES doctors(id))""")
    cur.execute("INSERT OR IGNORE INTO schedule VALUES(1, NULL, 1, '2025-10-01', '08:00', 'свободен')")
    cur.execute("INSERT OR IGNORE INTO schedule VALUES(2, 2, 1, '2025-10-01', '09:00', 'занят')")
    cur.execute("INSERT OR IGNORE INTO schedule VALUES(3, NULL, 2, '2025-10-02', '14:00', 'свободен')")
    cur.execute("INSERT OR IGNORE INTO schedule VALUES(4, 3, 3, '2025-10-03', '09:00', 'занят')")

    con.commit()
    print("БД успешно создано")


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
            ORDER BY s.name, d.nom_cab
        """)
        data = cur.fetchall()
    return data

def get_appointment():
    with sqlite3.connect("polic.db") as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("""
            SELECT 
                d.name AS doctor_name,
                s.name AS spec_name
            FROM doctors d
            JOIN specialize s ON d.id_spec = s.id
        """)
        data = [dict(row) for row in cur.fetchall()]
    doctors_data = [{"doctor_name": row["doctor_name"], "spec_name": row["spec_name"]} for row in data]

    specialties = sorted(list({row['spec_name'] for row in data}))
    return doctors_data, specialties




