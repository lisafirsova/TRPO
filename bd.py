import sqlite3

db = sqlite3.connect('polic.db')

cur = db.cursor()

cur.execute("CREATE TABLE specialize( id INTEGER, name TEXT, opis TEXT)")
cur.execute("INSERT INTO specialize VALUES(1,'Терапевт','Проводит первичную диагностику, назначает анализы и лечение. ')")
cur.execute("INSERT INTO specialize VALUES(2,'Проктолог','Специализируется на диагностике и лечении заболеваний толстой кишки, прямой кишки и заднего прохода.')")
cur.execute("INSERT INTO specialize VALUES(3,'Хирург','Хирург специализируется на оперативном лечении заболеваний и травм. ')")
db.commit()

cur.execute("CREATE TABLE doctors( id INTEGER, name TEXT, nom INTEGER, work_time TEXT)")
cur.execute("INSERT INTO doctors VALUES(1,'Волокитин Тимофей',201, '8.00-14.00')")
cur.execute("INSERT INTO doctors VALUES(2,'Акакий Харитонович',321, '14.00-20.00')")
cur.execute("INSERT INTO doctors VALUES(3,'Владимир Путин',412, '8.00-14.00')")
db.commit()

cur.execute("CREATE TABLE pacient( id_pac INTEGER, name TEXT, nom INTEGER, id_card INTEGER)")
cur.execute("INSERT INTO pacient VALUES(1,'Сергеев Альберт Альбертович',80295647812, 1)")
cur.execute("INSERT INTO pacient VALUES(2,'Миско Александр Сергеевич',80297817399, 2)")
cur.execute("INSERT INTO pacient VALUES(3,'Сватко Игорь Борисович',80291234354, 3)")
db.commit()

cur.execute("CREATE TABLE med_card(id_card INTEGER, id_pac INTEGER, name TEXT, spisok_zabol TEXT)")
cur.execute("INSERT INTO med_card VALUES(1,1,'Сергеев Альберт Альбертович', 'Грипп 20.03.2020, COVID-19 25.04.2021')")
cur.execute("INSERT INTO med_card VALUES(2,2,'Миско Александр Сергеевич', 'Язва желудка 12.03.2023')")
cur.execute("INSERT INTO med_card VALUES(3,3,'Сватко Игорь Борисович','Аппендицит 25.08.2025')")
db.commit()

cur.execute("CREATE TABLE talon(name_patient TEXT, name_doctor TEXT, kab INTEGER, data_priema TEXT, time_priema TEXT, status Text)")
cur.execute("INSERT INTO talon VALUES('Сергеев Альберт Альбертович','Акакий Акакиевич', 321, '30.09.2025','13.10', 'Неактивный')")
cur.execute("INSERT INTO talon VALUES('Миско Александр Сергеевич','Волокитин Тимофей', 201, '01.10.2025','15.00', 'Активный')")
cur.execute("INSERT INTO talon VALUES('Сватко Игорь Борисович','Владимир Путин', 412, '02.10.2025','9.00','Активный')")
db.commit()

db.close()