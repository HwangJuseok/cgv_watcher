import sqlite3
import os

DB_PATH = "data/user_data.db"

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # 영화관, 날짜, 상영관, 텔레그램 ID 조건까지 저장하도록 확장
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            platform TEXT NOT NULL DEFAULT 'ios',
            movie_code TEXT NOT NULL,
            theater_code TEXT NOT NULL,
            target_date TEXT NOT NULL,
            screen_type TEXT NOT NULL,
            telegram_id TEXT NOT NULL DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, movie_code, theater_code, target_date, screen_type)
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ 데이터베이스 스키마(구조) 업그레이드 완료!")

def add_subscription(user_id, platform, movie_code, theater_code, target_date, screen_type, telegram_id=""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO subscriptions (user_id, platform, movie_code, theater_code, target_date, screen_type, telegram_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (str(user_id), platform, movie_code, theater_code, target_date, screen_type, str(telegram_id)))
    conn.commit()
    conn.close()

def get_all_target_conditions():
    """크롤러가 감시해야 할 모든 유저들의 조건을 중복 없이 가져옴"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT movie_code, theater_code, target_date, screen_type FROM subscriptions')
    results = cursor.fetchall()
    conn.close()
    return [{"movie_code": r[0], "theater_code": r[1], "target_date": r[2], "screen_type": r[3]} for r in results]

def get_users_by_target(movie_code, theater_code, target_date, screen_type):
    """특정 조건의 예매가 열렸을 때 알림을 받을 유저 목록 반환 (텔레그램 ID 포함)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT user_id, platform, telegram_id FROM subscriptions 
        WHERE movie_code = ? AND theater_code = ? AND target_date = ? AND screen_type = ?
    ''', (movie_code, theater_code, target_date, screen_type))
    results = cursor.fetchall()
    conn.close()
    
    subscribers = {'telegram': [], 'ios': []}
    for user_id, platform, telegram_id in results:
        # 텔레그램 ID가 존재하는 경우 알림용 타겟 ID로 활용
        target_id = telegram_id if telegram_id else user_id
        if platform in subscribers:
            subscribers[platform].append(target_id)
    return subscribers

def get_user_subscriptions(user_id):
    """특정 유저가 등록한 감시 조건 목록 반환 (API용 JSON 포맷)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, movie_code, theater_code, target_date, screen_type, telegram_id 
        FROM subscriptions 
        WHERE user_id = ?
        ORDER BY created_at DESC
    ''', (str(user_id),))
    results = cursor.fetchall()
    conn.close()
    return [{
        "id": r[0],
        "movie_code": r[1], 
        "theater_code": r[2], 
        "target_date": r[3], 
        "screen_type": r[4],
        "telegram_id": r[5]
    } for r in results]

def delete_subscription(user_id, movie_code, theater_code, target_date, screen_type):
    """특정 감시 조건 삭제"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM subscriptions 
        WHERE user_id = ? AND movie_code = ? AND theater_code = ? AND target_date = ? AND screen_type = ?
    ''', (str(user_id), movie_code, theater_code, target_date, screen_type))
    conn.commit()
    conn.close()