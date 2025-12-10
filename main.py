from flask import Flask, request, jsonify, render_template, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

# ============================================================
# 初始化資料庫
# ============================================================
def init_user_db():
    # 若沒有 database 資料夾先建立
    if not os.path.exists("database"):
        os.makedirs("database")

    # 建立 user.db
    conn = sqlite3.connect("database/user.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            account TEXT UNIQUE,
            password TEXT
        );
    """)
    conn.commit()
    conn.close()

# 啟動時初始化
init_user_db()



# ============================================================
# 頁面路由
# ============================================================

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/register')
def register():
    return render_template("register.html")

@app.route('/shopping')
def shopping():
    return render_template("shopping.html")

@app.route('/shoppingcart')
def shoppingcart():
    return render_template("shoppingCart.html")

@app.route('/user')
def user():
    return render_template("user.html")



# ============================================================
# API：登入
# ============================================================

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    account = data.get("account")
    password = data.get("password")

    conn = sqlite3.connect("database/user.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE account=? AND password=?", (account, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify({"status": "success", "message": "登入成功"})
    else:
        return jsonify({"status": "fail", "message": "帳號或密碼錯誤"})


# ============================================================
# API：註冊
# ============================================================

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.json
    username = data.get("username")
    account = data.get("account")
    password = data.get("password")

    conn = sqlite3.connect("database/user.db")
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO users (username, account, password) VALUES (?, ?, ?)",
                       (username, account, password))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "註冊成功！"})
    
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"status": "fail", "message": "帳號已被使用"})


# ============================================================
# 啟動 Flask
# ============================================================

if __name__ == "__main__":
    app.run(debug=True)
