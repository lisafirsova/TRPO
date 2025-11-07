import sqlite3

with sqlite3.connect("polic.db") as con:
    cur = con.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")

#SPECIALIZE
    cur.execute("""
    CREATE TABLE IF NOT EXISTS specialize (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        opis TEXT
    )
    """)
    cur.execute("INSERT OR IGNORE INTO specialize VALUES(1,'Терапевт','Проводит первичную диагностику, назначает анализы и лечение.')")
    cur.execute("INSERT OR IGNORE INTO specialize VALUES(2,'Проктолог','Диагностика и лечение заболеваний толстой и прямой кишки.')")
    cur.execute("INSERT OR IGNORE INTO specialize VALUES(3,'Хирург','Оперативное лечение заболеваний и травм.')")

#DOCTORS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS doctors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        nom_cab INTEGER,
        work_time TEXT,
        id_spec INTEGER,
        FOREIGN KEY (id_spec) REFERENCES specialize(id)
    )
    """)
    cur.execute("INSERT OR IGNORE INTO doctors VALUES(1,'Волокитин Тимофей',201,'8.00-14.00',1)")
    cur.execute("INSERT OR IGNORE INTO doctors VALUES(2,'Акакий Харитонович',321,'14.00-20.00',2)")
    cur.execute("INSERT OR IGNORE INTO doctors VALUES(3,'Владимир Путин',412,'8.00-14.00',3)")

#PACIENT
    cur.execute("""
    CREATE TABLE IF NOT EXISTS pacient (
        id_pac INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        nom INTEGER,
        id_card INTEGER
    )
    """)
    cur.execute("INSERT OR IGNORE INTO pacient VALUES(1,'Сергеев Альберт Альбертович',80295647812,1)")
    cur.execute("INSERT OR IGNORE INTO pacient VALUES(2,'Миско Александр Сергеевич',80297817399,2)")
    cur.execute("INSERT OR IGNORE INTO pacient VALUES(3,'Сватко Игорь Борисович',80291234354,3)")

#MED_CARD
    cur.execute("""
    CREATE TABLE IF NOT EXISTS med_card (
        id_card INTEGER PRIMARY KEY AUTOINCREMENT,
        id_pac INTEGER,
        spisok_zabol TEXT,
        FOREIGN KEY (id_pac) REFERENCES pacient(id_pac)
    )
    """)
    cur.execute("INSERT OR IGNORE INTO med_card VALUES(1,1,'Грипп 20.03.2020, COVID-19 25.04.2021')")
    cur.execute("INSERT OR IGNORE INTO med_card VALUES(2,2,'Язва желудка 12.03.2023')")
    cur.execute("INSERT OR IGNORE INTO med_card VALUES(3,3,'Аппендицит 25.08.2025')")

#TALON
    cur.execute("""
    CREATE TABLE IF NOT EXISTS talon (
        id_talon INTEGER PRIMARY KEY AUTOINCREMENT,
        id_pac INTEGER,
        id_doctor INTEGER,
        data_priema TEXT,
        time_priema TEXT,
        status TEXT,
        FOREIGN KEY (id_pac) REFERENCES pacient(id_pac),
        FOREIGN KEY (id_doctor) REFERENCES doctors(id)
    )
    """)
    cur.execute("INSERT OR IGNORE INTO talon VALUES(1,1,2,'30.09.2025','13:10','Неактивный')")
    cur.execute("INSERT OR IGNORE INTO talon VALUES(2,2,1,'01.10.2025','15:00','Активный')")
    cur.execute("INSERT OR IGNORE INTO talon VALUES(3,3,3,'02.10.2025','09:00','Активный')")

#SCHEDULE
    cur.execute("""
    CREATE TABLE IF NOT EXISTS schedule (
        id_rasp INTEGER PRIMARY KEY AUTOINCREMENT,
        id_talon INTEGER,
        id_doctor INTEGER NOT NULL,
        data_priema TEXT NOT NULL,
        time_priema TEXT NOT NULL,
        status TEXT CHECK(status IN ('свободен','занят')) DEFAULT 'свободен',
        FOREIGN KEY (id_talon) REFERENCES talon(id_talon),
        FOREIGN KEY (id_doctor) REFERENCES doctors(id)
    )
    """)
    cur.execute("INSERT OR IGNORE INTO schedule VALUES(1, NULL, 1, '2025-10-01', '08:00', 'свободен')")
    cur.execute("INSERT OR IGNORE INTO schedule VALUES(2, 2, 1, '2025-10-01', '09:00', 'занят')")
    cur.execute("INSERT OR IGNORE INTO schedule VALUES(3, NULL, 2, '2025-10-02', '14:00', 'свободен')")
    cur.execute("INSERT OR IGNORE INTO schedule VALUES(4, 3, 3, '2025-10-03', '09:00', 'занят')")

    con.commit()
    print("БД успешно создано")
