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
def add_to_cart():
    data = request.get_json()
    user_id = session.get("user_id")
    item_id = data.get("item_id")
    quantity = data.get("quantity", 1)

    if not user_id:
        return jsonify({"error": "未登入"}), 401

    conn = sqlite3.connect("database/app.db")
    cursor = conn.cursor()

    # 檢查是否已經在購物車中
    cursor.execute("SELECT quantity FROM Cart WHERE user_id=? AND item_id=?", (user_id, item_id))
    row = cursor.fetchone()

    if row:
        # 更新數量
        new_qty = row[0] + quantity
        cursor.execute("UPDATE Cart SET quantity=? WHERE user_id=? AND item_id=?", (new_qty, user_id, item_id))
    else:
        # 新增
        cursor.execute("INSERT INTO Cart (user_id, item_id, quantity) VALUES (?, ?, ?)",
                       (user_id, item_id, quantity))

    conn.commit()
    conn.close()

    return jsonify({"message": "加入購物車成功"})

# ============================================================
# API：查看購物車
# ============================================================
@app.route('/api/cart/view')
def view_cart():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify([])

    conn = sqlite3.connect("database/app.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            Items.item_id, 
            Items.name, 
            Items.price, 
            Items.image_path, 
            Cart.quantity
        FROM Cart
        JOIN Items ON Cart.item_id = Items.item_id
        WHERE Cart.user_id=?
    """, (user_id,))

    rows = cursor.fetchall()
    conn.close()

    cart = []
    for item in rows:
        cart.append({
            "item_id": item[0],
            "name": item[1],
            "price": item[2],
            "image_path": item[3],   # ← 這裡才是 image_path
            "quantity": item[4]      # ← 這裡才是 quantity
        })

    return jsonify(cart)

# ============================================================
# API：移除購物車項目
# ============================================================
@app.route('/api/cart/remove', methods=['POST'])
def remove_from_cart():
    data = request.get_json()
    user_id = session.get("user_id")
    item_id = data.get("item_id")

    if not user_id:
        return jsonify({"error": "未登入"}), 401

    conn = sqlite3.connect("database/app.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM Cart WHERE user_id=? AND item_id=?", (user_id, item_id))

    conn.commit()
    conn.close()

    return jsonify({"message": "已移除"})

# ============================================================
# API：購務車調整數量
# ============================================================
@app.route('/api/cart/update_quantity', methods=['POST'])
def update_cart_quantity():
    data = request.get_json()
    user_id = session.get("user_id")
    item_id = data.get("item_id")
    quantity = data.get("quantity")

    if not user_id:
        return jsonify({"error": "未登入"}), 401

    conn = sqlite3.connect("database/app.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE Cart 
        SET quantity=? 
        WHERE user_id=? AND item_id=?
    """, (quantity, user_id, item_id))

    conn.commit()
    conn.close()

    return jsonify({"message": "數量已更新"})

# ============================================================
# API：結帳
# ============================================================
@app.route('/api/cart/checkout', methods=['POST'])
def checkout():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "未登入"}), 401

    data = request.get_json()
    selected_items = data.get("items", [])
    print("收到 items:", selected_items)

    if not selected_items:
        return jsonify({"error": "沒有選擇商品"}), 400

    conn = sqlite3.connect("database/app.db")
    cursor = conn.cursor()

    placeholders = ",".join("?" * len(selected_items))

    # 1️⃣ 先 SELECT
    query = f"""
        SELECT Items.item_id, Items.price, Cart.quantity
        FROM Cart
        JOIN Items ON Cart.item_id = Items.item_id
        WHERE Cart.user_id=? AND Cart.item_id IN ({placeholders})
    """
    cursor.execute(query, [user_id, *selected_items])
    cart_items = cursor.fetchall()

    if not cart_items:
        return jsonify({"error": "選擇的商品不存在"}), 400

    # 2️⃣ 計算總金額
    total_price = sum(item[1] * item[2] for item in cart_items)

    # 3️⃣ 建立訂單
    cursor.execute("""
        INSERT INTO Orders (user_id, total_price)
        VALUES (?, ?)
    """, (user_id, total_price))
    order_id = cursor.lastrowid

    # 4️⃣ 建立訂單明細 + 扣庫存
    for item_id, price, qty in cart_items:
        cursor.execute("""
            INSERT INTO OrderDetails (order_id, item_id, quantity, price)
            VALUES (?, ?, ?, ?)
        """, (order_id, item_id, qty, price))

        cursor.execute("""
            UPDATE Items
            SET stock = stock - ?
            WHERE item_id=?
        """, (qty, item_id))

    # 5️⃣ 最後才 DELETE
    cursor.execute(
        f"DELETE FROM Cart WHERE user_id=? AND item_id IN ({placeholders})",
        [user_id, *selected_items]
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "結帳完成"})

# ============================================================
# 啟動 Flask
# ============================================================

if __name__ == "__main__":
    init_db()       # 建立表格
    load_items()    # 匯入道具
    print("資料庫初始化 + 道具匯入完成！")
    app.run(host='0.0.0.0', port=5000)
