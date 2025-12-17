import sqlite3
import os
import hashlib

DB_PATH = "database/app.db"

def get_connection():
    if not os.path.exists("database"):
        os.makedirs("database")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def reset_database():
    # ============================
    # 刪除舊資料庫
    # ============================
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("🗑️ 已刪除舊的 app.db")

    conn = get_connection()
    cursor = conn.cursor()

    # ============================
    # 建立 Users 表
    # ============================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        account TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        strength INTEGER DEFAULT 0,
        intelligence INTEGER DEFAULT 0,
        luck INTEGER DEFAULT 0,
        money INTEGER DEFAULT 10000,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ============================
    # 建立 Items 表
    # ============================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Items (
        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        rarity TEXT,
        price INTEGER NOT NULL,
        stock INTEGER NOT NULL,
        effect_description TEXT,
        strength_bonus INTEGER DEFAULT 0,
        intelligence_bonus INTEGER DEFAULT 0,
        luck_bonus INTEGER DEFAULT 0,
        image_path TEXT
    )
    """)

    # ============================
    # 建立 Cart 表
    # ============================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Cart (
        cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        item_id INTEGER,
        quantity INTEGER,
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES Users(user_id),
        FOREIGN KEY(item_id) REFERENCES Items(item_id)
    )
    """)

    # ============================
    # 建立 Orders 表
    # ============================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        total_price INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES Users(user_id)
    )
    """)

    # ============================
    # 建立 OrderDetails 表
    # ============================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS OrderDetails (
        detail_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        item_id INTEGER,
        quantity INTEGER,
        price INTEGER,
        FOREIGN KEY(order_id) REFERENCES Orders(order_id),
        FOREIGN KEY(item_id) REFERENCES Items(item_id)
    )
    """)

    # ============================
    # 建立 Inventory 表
    # ============================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Inventory (
        inventory_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        item_id INTEGER,
        quantity INTEGER,
        is_used BOOLEAN DEFAULT 0,
        FOREIGN KEY(user_id) REFERENCES Users(user_id),
        FOREIGN KEY(item_id) REFERENCES Items(item_id)
    )
    """)

    conn.commit()

    # ============================
    # 插入預設使用者
    # ============================
    default_users = [
        ("test1", "測試人員1", "test1", 0, 0, 0),
        ("test2", "測試人員2", "test2", 0, 0, 0),
        ("npc1", "路人甲", "npc1", 10, 10, 10),
        ("npc2", "路人乙", "npc2", 10, 10, 10)
    ]

    for account, name, password, str_val, int_val, luck_val in default_users:
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute("""
            INSERT INTO Users (account, name, password_hash, strength, intelligence, luck)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (account, name, password_hash, str_val, int_val, luck_val))

    conn.commit()

    # ============================
    # 匯入 Items（items.sql）
    # ============================
    if os.path.exists("database/items.sql"):
        with open("database/items.sql", "r", encoding="utf-8") as f:
            cursor.executescript(f.read())
        conn.commit()
        print("📦 已匯入 items.sql")
    else:
        print("⚠️ 找不到 items.sql，跳過匯入")

    conn.close()
    print("✅ 資料庫重建完成！")


if __name__ == "__main__":
    reset_database()
