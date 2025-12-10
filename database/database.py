import sqlite3
import os

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

    # 使用者表
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

    # 道具表
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

    # 購物車表
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

    # 訂單表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        total_price INTEGER,
        FOREIGN KEY(user_id) REFERENCES Users(user_id)
    )
    """)

    # 訂單明細表
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

    # 包包表
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

