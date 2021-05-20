import os
import sqlite3
import threading


WORKING_DIR = os.path.dirname(os.path.realpath(__file__))
DB_DIR = os.path.join(WORKING_DIR, 'database.db')

db_locker = threading.Semaphore(1)

def check_db():
    conn = sqlite3.connect(DB_DIR)
    cursor = conn.cursor()

    def create_table():
        execute_command = 'CREATE TABLE IF NOT EXISTS items ('+\
                    'item_id INTEGER PRIMARY KEY NOT NULL, '+\
                    'course_id INTEGER, '+\
                    'finished TINYINT NOT NULL DEFAULT 0, '\
                    "created_time TimeStamp NOT NULL DEFAULT (datetime('now','localtime')))"
        cursor.execute(execute_command)

    try:
        cursor.execute('SELECT COUNT(*) FROM pages')
    except sqlite3.OperationalError as e:
        if 'no such table' in str(e):
            create_table()
            print('Database initialized')
        else:
            print('unknown error')
            exit()
    else:
        print('Database checked')

    cursor.close()
    conn.commit()
    conn.close()

def read(item_id: int):
    db_locker.acquire()
    conn = sqlite3.connect(DB_DIR)
    cursor = conn.cursor()

    cursor.execute("SELECT finished FROM items WHERE item_id=:item_id", {'item_id': item_id})

    try:
        item_finished = cursor.fetchall()[0][0]
    except IndexError as e:
        cursor.close()
        conn.close()
        db_locker.release()
        print(f'data not found - {str(e)}')
        return False

    cursor.close()
    conn.close()
    db_locker.release()

    return item_finished

def insert(item_id: int, course_id: int):
	db_locker.acquire()
	item_dict = {
		'item_id': item_id,
		'course_id': course_id,
	}

	conn = sqlite3.connect(DB_DIR)
	cursor = conn.cursor()

	execute_command = f"INSERT INTO items (item_id, course_id)"
	execute_command += f" VALUES (:item_id, :course_id)"

	try:
		cursor.execute(execute_command, item_dict)
	except sqlite3.IntegrityError as e:
		print(f'item already exists in database - {str(e)}')

	cursor.close()
	conn.commit()
	conn.close()
	db_locker.release()

def update(item_id: int, finished: bool):
    finished = finished * 1
    item_dict = {
        'item_id': item_id,
        'finished': finished,
    }

    db_locker.acquire()
    conn = sqlite3.connect(DB_DIR)
    cursor = conn.cursor()

    try:
        execute_command="UPDATE items SET finished=:finished WHERE item_id=:item_id"
        cursor.execute(execute_command, item_dict)
    except IndexError as e:
        cursor.close()
        conn.commit()
        conn.close()
        db_locker.release()
        print(f'data not found - {str(e)}')

    cursor.close()
    conn.commit()
    conn.close()
    db_locker.release()

def exist(item_id: int):
    db_locker.acquire()
    conn = sqlite3.connect(DB_DIR)
    cursor = conn.cursor()

    cursor.execute("SELECT finished FROM items WHERE item_id=:item_id", {'item_id': item_id})

    try:
        cursor.fetchall()[0]
    except IndexError as e:
        cursor.close()
        conn.close()
        db_locker.release()
        return False

    cursor.close()
    conn.close()
    db_locker.release()

    return True
