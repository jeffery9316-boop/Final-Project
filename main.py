from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import sqlite3
import hashlib
from database.database import init_db, load_items


app = Flask(__name__, static_folder='static')
app.secret_key = "your_secret_key_here"   # ★ Session 必須使用

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
    # 如果尚未登入 → 不能訪問
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # ★ 傳送登入使用者的姓名
    return render_template("shopping.html", username=session.get('name'))

@app.route('/shoppingcart')
def shoppingcart():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # ★ 傳送登入姓名到購物車頁面
    return render_template("shoppingCart.html", username=session.get('name'))

@app.route('/user')
def user():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # ★ 傳送登入姓名到使用者頁面
    return render_template("user.html", username=session.get('name'))

# ============================================================
# 登出功能
# ============================================================

@app.route('/logout')
def logout():
    session.clear()   # 清除登入狀態
    return redirect(url_for('login'))


# ============================================================
# API：登入
# ============================================================

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    account = data.get("account")
    password = data.get("password")

    # 密碼 hash
    password_hash = hashlib.sha256(password.encode()).hexdigest()

    conn = sqlite3.connect("database/app.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT user_id, account, name FROM Users WHERE account=? AND password_hash=?",
        (account, password_hash)
    )
    user = cursor.fetchone()
    conn.close()

    if user:
        # ★ 記住登入狀態
        session['user_id'] = user[0]
        session['account'] = user[1]
        session['name'] = user[2]

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
    account = data.get("account")
    name = data.get("name")
    password = data.get("password")

    # 密碼 hash
    password_hash = hashlib.sha256(password.encode()).hexdigest()

    conn = sqlite3.connect("database/app.db")
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO Users (account, name, password_hash) VALUES (?, ?, ?)",
            (account, name, password_hash)
        )
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "註冊成功！"})

    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"status": "fail", "message": "帳號已被使用"})


# ============================================================
# API：商品列表
# ============================================================

@app.route('/api/items', methods=['GET'])
def api_items():
    conn = sqlite3.connect("database/app.db")
    cursor = conn.cursor()
    cursor.execute("SELECT item_id, name, rarity, price, effect_description, image_path, stock FROM Items")
    items = cursor.fetchall()
    conn.close()

    result = []
    for item in items:
        result.append({
            "item_id": item[0],
            "name": item[1],
            "rarity": item[2],
            "price": item[3],
            "effect_description": item[4],
            "image_path": item[5],
            "stock": item[6]

        })
    return jsonify(result)

# ============================================================
# API：商品篩選
# ============================================================

@app.route('/api/filter_items', methods=['POST'])
def api_filter_items():
    data = request.json
    rarities = data.get("rarities", [])
    strength = int(data.get("strength", 0))
    intelligence = int(data.get("intelligence", 0))
    luck = int(data.get("luck", 0))

    conn = sqlite3.connect("database/app.db")
    cursor = conn.cursor()

    query = """
        SELECT item_id, name, rarity, price, effect_description, image_path, stock,
               strength_bonus, intelligence_bonus, luck_bonus
        FROM Items
        WHERE strength_bonus >= ?
        AND intelligence_bonus >= ?
        AND luck_bonus >= ?
    """

    params = [strength, intelligence, luck]

    if rarities:
        placeholders = ",".join("?" * len(rarities))
        query += f" AND rarity IN ({placeholders})"
        params.extend(rarities)

    cursor.execute(query, params)
    items = cursor.fetchall()
    conn.close()

    result = []
    for item in items:
        result.append({
            "item_id": item[0],
            "name": item[1],
            "rarity": item[2],
            "price": item[3],
            "effect_description": item[4],
            "image_path": item[5],
            "stock": item[6],
            "strength_bonus": item[7],
            "intelligence_bonus": item[8],
            "luck_bonus": item[9],
        })

    return jsonify(result)



# ============================================================
# API：加入購物車
# ============================================================

@app.route('/api/cart/add', methods=['POST'])
def api_cart_add():
    data = request.json
    user_id = data.get("user_id")
    item_id = data.get("item_id")
    quantity = data.get("quantity", 1)

    conn = sqlite3.connect("database/app.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Cart (user_id, item_id, quantity) VALUES (?, ?, ?)",
                   (user_id, item_id, quantity))
    conn.commit()
    conn.close()

    return jsonify({"status": "success", "message": "已加入購物車"})


# ============================================================
# 啟動 Flask
# ============================================================

if __name__ == "__main__":
    init_db()       # 建立表格
    load_items()    # 匯入道具
    print("資料庫初始化 + 道具匯入完成！")
    app.run(debug=True)
