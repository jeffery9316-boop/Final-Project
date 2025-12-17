from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import sqlite3
import hashlib
from database.database import get_connection, init_db, load_items


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

@app.route("/orders")
def orders():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    conn = get_connection()
    cursor = conn.cursor()

    # 查詢使用者資料
    cursor.execute("""
        SELECT account, name, created_at, strength, intelligence, luck
        FROM Users
        WHERE user_id=?
    """, (user_id,))
    user = cursor.fetchone()

    # 查詢訂單
    cursor.execute("""
        SELECT order_id, total_price, created_at
        FROM Orders
        WHERE user_id=?
        ORDER BY created_at DESC
    """, (user_id,))
    orders = cursor.fetchall()

    conn.close()

    return render_template("orders.html", user=user, orders=orders)

@app.route('/user')
def user():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_connection()
    cursor = conn.cursor()

    # 取得使用者資料
    cursor.execute("SELECT * FROM Users WHERE user_id = ?", (session["user_id"],))
    user = cursor.fetchone()

    # 取得包包（Inventory）
    cursor.execute("""
        SELECT i.*, inv.quantity
        FROM Inventory inv
        JOIN Items i ON inv.item_id = i.item_id
        WHERE inv.user_id = ?
    """, (session["user_id"],))
    inventory = cursor.fetchall()

    conn.close()

    return render_template("user.html", user=user, inventory=inventory)

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
# API：註冊（加入能力點數）
# ============================================================
@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.json
    account = data.get("account")
    name = data.get("name")
    password = data.get("password")

    # 新增能力欄位
    strength = int(data.get("strength", 0))
    intelligence = int(data.get("intelligence", 0))
    luck = int(data.get("luck", 0))

    # 驗證能力點數總和
    if strength + intelligence + luck > 30:
        return jsonify({"status": "fail", "message": "能力點數總和不能超過 30 點！"})

    # 密碼 hash
    password_hash = hashlib.sha256(password.encode()).hexdigest()

    conn = sqlite3.connect("database/app.db")
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO Users (account, name, password_hash, strength, intelligence, luck)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (account, name, password_hash, strength, intelligence, luck)
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

    return jsonify({"message": "已移除商品"})

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
# API：結帳（含寫入 Inventory）
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

    # 1️⃣ 查詢購物車內容
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
    total_price = sum(price * qty for _, price, qty in cart_items)

    # 3️⃣ 建立訂單（含 created_at）
    cursor.execute("""
        INSERT INTO Orders (user_id, total_price, created_at)
        VALUES (?, ?, datetime('now', 'localtime'))
    """, (user_id, total_price))
    order_id = cursor.lastrowid

    # 4️⃣ 建立訂單明細 + 扣庫存 + 寫入 Inventory
    for item_id, price, qty in cart_items:

        # 建立訂單明細
        cursor.execute("""
            INSERT INTO OrderDetails (order_id, item_id, quantity, price)
            VALUES (?, ?, ?, ?)
        """, (order_id, item_id, qty, price))

        # 扣庫存
        cursor.execute("""
            UPDATE Items
            SET stock = stock - ?
            WHERE item_id=?
        """, (qty, item_id))

        # 寫入 Inventory（包包）
        cursor.execute("""
            SELECT quantity FROM Inventory
            WHERE user_id=? AND item_id=?
        """, (user_id, item_id))
        existing = cursor.fetchone()

        if existing:
            cursor.execute("""
                UPDATE Inventory
                SET quantity = quantity + ?
                WHERE user_id=? AND item_id=?
            """, (qty, user_id, item_id))
        else:
            cursor.execute("""
                INSERT INTO Inventory (user_id, item_id, quantity)
                VALUES (?, ?, ?)
            """, (user_id, item_id, qty))

    # 5️⃣ 清空購物車中已購買的項目
    cursor.execute(
        f"DELETE FROM Cart WHERE user_id=? AND item_id IN ({placeholders})",
        [user_id, *selected_items]
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "結帳完成"})

# ============================================================
# API：查詢訂單明細
# ============================================================
@app.route("/api/order_details/<int:order_id>")
def order_details(order_id):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "未登入"}), 401

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT Items.name, OrderDetails.quantity, OrderDetails.price
        FROM OrderDetails
        JOIN Items ON OrderDetails.item_id = Items.item_id
        WHERE OrderDetails.order_id=?
    """, (order_id,))
    details = cursor.fetchall()

    conn.close()

    return jsonify([dict(row) for row in details])

# ============================================================
# API：取得使用者包包
# ============================================================
@app.route("/api/inventory")
def api_inventory():
    if "user_id" not in session:
        return jsonify({"error": "未登入"}), 401

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT i.item_id, i.name, i.effect_description, i.image_path,
               i.strength_bonus, i.intelligence_bonus, i.luck_bonus,
               inv.quantity
        FROM Inventory inv
        JOIN Items i ON inv.item_id = i.item_id
        WHERE inv.user_id = ?
    """, (session["user_id"],))

    items = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify(items)

# ============================================================
# API：使用道具
# ============================================================
@app.route("/api/use_item", methods=["POST"])
def use_item():
    if "user_id" not in session:
        return jsonify({"error": "未登入"}), 401

    data = request.get_json()
    item_id = data.get("item_id")
    qty = data.get("quantity", 1)

    conn = get_connection()
    cursor = conn.cursor()

    user_id = session["user_id"]

    # 取得道具資訊
    cursor.execute("""
        SELECT strength_bonus, intelligence_bonus, luck_bonus
        FROM Items WHERE item_id=?
    """, (item_id,))
    item = cursor.fetchone()

    if not item:
        return jsonify({"error": "道具不存在"}), 400

    str_b, int_b, luck_b = item

    # 檢查持有數量
    cursor.execute("""
        SELECT quantity FROM Inventory
        WHERE user_id=? AND item_id=?
    """, (user_id, item_id))
    inv = cursor.fetchone()

    # 如果沒有這筆資料 → 直接回傳
    if not inv:
        return jsonify({"error": "道具數量不足"}), 400

    # 如果數量是 0 → 刪除並回傳錯誤
    if inv["quantity"] == 0:
        cursor.execute("""
            DELETE FROM Inventory
            WHERE user_id=? AND item_id=?
        """, (user_id, item_id))
        conn.commit()
        return jsonify({"error": "道具數量不足"}), 400

    # 如果數量不足以使用
    if inv["quantity"] < qty:
        return jsonify({"error": "道具數量不足"}), 400

    # 扣除道具
    cursor.execute("""
        UPDATE Inventory
        SET quantity = quantity - ?
        WHERE user_id=? AND item_id=?
    """, (qty, user_id, item_id))

    # 如果數量變 0 → 刪除這筆資料
    cursor.execute("""
        DELETE FROM Inventory
        WHERE user_id=? AND item_id=? AND quantity <= 0
    """, (user_id, item_id))

    # 更新能力值（乘上使用數量）
    cursor.execute("""
        UPDATE Users
        SET strength = strength + ?,
            intelligence = intelligence + ?,
            luck = luck + ?
        WHERE user_id=?
    """, (str_b * qty, int_b * qty, luck_b * qty, user_id))

    # 回傳最新能力值
    cursor.execute("""
        SELECT strength, intelligence, luck
        FROM Users WHERE user_id=?
    """, (user_id,))
    new_stats = cursor.fetchone()

    conn.commit()
    conn.close()

    return jsonify({
        "message": "使用成功",
        "stats": {
            "strength": new_stats["strength"],
            "intelligence": new_stats["intelligence"],
            "luck": new_stats["luck"]
        }
    })


# ============================================================
# 啟動 Flask
# ============================================================

if __name__ == "__main__":
    init_db()       # 建立表格
    load_items()    # 匯入道具
    print("資料庫初始化 + 道具匯入完成！")
    app.run(host='0.0.0.0', port=5000)
