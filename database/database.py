import sqlite3
import os
import hashlib

def get_connection():
    # 如果 database 資料夾不存在，先建立
    if not os.path.exists("database"):
        os.makedirs("database")

    # 自動建立 app.db（如果不存在）
    conn = sqlite3.connect("database/app.db")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
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
        order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        total_price INTEGER,
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
        try:
            cursor.execute("""
                INSERT INTO Users (account, name, password_hash, strength, intelligence, luck)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (account, name, password_hash, str_val, int_val, luck_val))
        except sqlite3.IntegrityError:
            pass  # 已存在就跳過

    conn.commit()
    conn.close()


def load_items():
    conn = get_connection()
    cursor = conn.cursor()

    # 檢查 Items 表是否已有資料
    cursor.execute("SELECT COUNT(*) FROM Items")
    count = cursor.fetchone()[0]

    if count == 0:  # 只有在空表時才匯入
        with open("database/items.sql", "r", encoding="utf-8") as f:
            cursor.executescript(f.read())
        conn.commit()
        print("道具已成功匯入 Items 表！")
    else:
        print("Items 表已有資料，跳過匯入。")

    conn.close()
