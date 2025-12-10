from flask import Flask, request, jsonify, render_template, redirect, url_for
import sqlite3
import hashlib
from database.database import init_db, load_items


app = Flask(__name__)

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
    account = data.get("account")   # 使用者輸入的帳號
    password = data.get("password")

    # 密碼 hash
    password_hash = hashlib.sha256(password.encode()).hexdigest()

    conn = sqlite3.connect("database/app.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, account, name FROM Users WHERE account=? AND password_hash=?", 
                   (account, password_hash))
    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify({
            "status": "success",
            "message": "登入成功",
            "user_id": user[0],
            "account": user[1],
            "name": user[2]
        })
    else:
        return jsonify({"status": "fail", "message": "帳號或密碼錯誤"})


# ============================================================
# API：註冊
# ============================================================

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.json
    account = data.get("account")   # 登入帳號（唯一）
    name = data.get("name")         # 使用者名字（顯示用）
    password = data.get("password")

    # 密碼 hash
    password_hash = hashlib.sha256(password.encode()).hexdigest()

    conn = sqlite3.connect("database/app.db")
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO Users (account, name, password_hash) VALUES (?, ?, ?)",
                       (account, name, password_hash))
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
    init_db()       # 建立表格
    load_items()    # 匯入道具
    print("資料庫初始化 + 道具匯入完成！")
    app.run(debug=True)
