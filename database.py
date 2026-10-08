import sqlite3
from datetime import date, timedelta
from pathlib import Path
import json

DB_PATH = Path("data/toilet.db")

def init_db():
    """DB初期化＆メンバー投入"""
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("""CREATE TABLE IF NOT EXISTS members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        gender TEXT NOT NULL
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        role TEXT NOT NULL,
        member_name TEXT NOT NULL
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS round_status (
        role TEXT NOT NULL,
        member_name TEXT NOT NULL,
        done INTEGER DEFAULT 0,
        PRIMARY KEY (role, member_name)
    )""")
    
    c.execute("SELECT COUNT(*) FROM members")
    if c.fetchone()[0] == 0:
        with open("members.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        for name in data["men"]:
            c.execute("INSERT INTO members (name, gender) VALUES (?, ?)", (name, "M"))
        for name in data["women"]:
            c.execute("INSERT INTO members (name, gender) VALUES (?, ?)", (name, "F"))
        
        for name in data["men"]:
            c.execute("INSERT INTO round_status VALUES (?, ?, 0)", ("Men", name))
            c.execute("INSERT INTO round_status VALUES (?, ?, 0)", ("Guest", name))
        for name in data["women"]:
            c.execute("INSERT INTO round_status VALUES (?, ?, 0)", ("Women", name))
    
    conn.commit()
    conn.close()

def get_members(gender=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if gender:
        c.execute("SELECT name FROM members WHERE gender=?", (gender,))
        result = [r[0] for r in c.fetchall()]
    else:
        c.execute("SELECT name, gender FROM members")
        result = c.fetchall()
    conn.close()
    return result

def get_recent_winners(role, days):
    """直近N日間の当選者を取得"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    threshold = (date.today() - timedelta(days=days)).isoformat()
    c.execute("SELECT DISTINCT member_name FROM history WHERE role=? AND date > ?",
              (role, threshold))
    result = [r[0] for r in c.fetchall()]
    conn.close()
    return result

def get_round_done(role):
    """今周当選済みのメンバー"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT member_name FROM round_status WHERE role=? AND done=1", (role,))
    result = [r[0] for r in c.fetchall()]
    conn.close()
    return result

def get_round_counts(role):
    """今周の進捗（済み/全体）"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM round_status WHERE role=?", (role,))
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM round_status WHERE role=? AND done=1", (role,))
    done = c.fetchone()[0]
    conn.close()
    return done, total

def save_result(winners):
    """抽選結果を保存＋round_status更新"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    today = date.today().isoformat()
    
    c.execute("DELETE FROM history WHERE date=?", (today,))
    
    for role, name in winners.items():
        if name:
            c.execute("INSERT INTO history (date, role, member_name) VALUES (?, ?, ?)",
                      (today, role, name))
            c.execute("UPDATE round_status SET done=1 WHERE role=? AND member_name=?",
                      (role, name))
    
    for role in ["Men", "Guest", "Women"]:
        c.execute("SELECT COUNT(*) FROM round_status WHERE role=? AND done=0", (role,))
        if c.fetchone()[0] == 0:
            c.execute("UPDATE round_status SET done=0 WHERE role=?", (role,))
    
    conn.commit()
    conn.close()

def get_history(limit=7):
    """直近N日の履歴"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT date, role, member_name FROM history ORDER BY date DESC LIMIT ?",
              (limit * 3,))
    result = c.fetchall()
    conn.close()
    return result

def reset_round(role=None):
    """今周リセット"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if role:
        c.execute("UPDATE round_status SET done=0 WHERE role=?", (role,))
    else:
        c.execute("UPDATE round_status SET done=0")
    conn.commit()
    conn.close()

def rename_member(old_name, new_name):
    """メンバーのあだ名を変更（members / history / round_status 全部更新）"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE members SET name=? WHERE name=?", (new_name, old_name))
    c.execute("UPDATE history SET member_name=? WHERE member_name=?", (new_name, old_name))
    c.execute("UPDATE round_status SET member_name=? WHERE member_name=?", (new_name, old_name))
    conn.commit()
    conn.close()
