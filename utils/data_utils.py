import sqlite3
import json
import logging

logging.basicConfig(level=logging.DEBUG)

DATABASE_NAME = "dodo_bot.db"


def create_user_table():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            tg_user_id INTEGER PRIMARY KEY,
            token TEXT,
            code_verifier TEXT,
            name TEXT,
            subs TEXT,
             schedule_times TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_user_data(tg_user_id):
   conn = sqlite3.connect(DATABASE_NAME)
   cursor = conn.cursor()
   cursor.execute("SELECT * FROM users WHERE tg_user_id = ?", (tg_user_id,))
   row = cursor.fetchone()
   conn.close()
   if row:
       return {
          "tg_user_id": row[0],
          "token": row[1],
          "code_verifier": row[2],
          "name":row[3],
          "subs":json.loads(row[4]) if row[4] else [],
           "schedule_times": json.loads(row[5]) if row[5] else []
        }
   return None

def update_user_token(tg_user_id, token):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO users (tg_user_id, token) VALUES (?, ?)", (tg_user_id, token))
    conn.commit()
    conn.close()


def update_user_code_verifier(tg_user_id, code_verifier):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO users (tg_user_id, code_verifier) VALUES (?, ?)", (tg_user_id, code_verifier))
    conn.commit()
    conn.close()

def update_user_name(tg_user_id, name):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO users (tg_user_id, name) VALUES (?, ?)", (tg_user_id, name))
    conn.commit()
    conn.close()

def update_user_subscriptions(tg_user_id, subs):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET subs = ? WHERE tg_user_id = ?", (json.dumps(subs), tg_user_id))
    conn.commit()
    conn.close()

def update_user_report_schedule(tg_user_id, schedule_times):
     conn = sqlite3.connect(DATABASE_NAME)
     cursor = conn.cursor()
     cursor.execute("UPDATE users SET schedule_times = ? WHERE tg_user_id = ?", (json.dumps(schedule_times), tg_user_id))
     conn.commit()
     conn.close()

def get_user_subscriptions(tg_user_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT subs FROM users WHERE tg_user_id = ?", (tg_user_id,))
    row = cursor.fetchone()
    conn.close()
    if row and row[0]:
        return json.loads(row[0])
    return []

def get_user_report_schedule(tg_user_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT schedule_times FROM users WHERE tg_user_id = ?", (tg_user_id,))
    row = cursor.fetchone()
    conn.close()
    if row and row[0]:
        return json.loads(row[0])
    return []