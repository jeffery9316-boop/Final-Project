document.addEventListener("DOMContentLoaded", loadCart);

let cartData = [];

// ================================
// 載入購物車內容
// ================================
async function loadCart() {
    const res = await fetch("/api/cart/view");
    cartData = await res.json();

    const container = document.getElementById("cartItems");
    container.innerHTML = "";

    cartData.forEach(item => {
        const div = document.createElement("div");
        div.className = "cart-item";

        div.innerHTML = `
            <input type="checkbox"
                   class="cart-check"
                   data-item-id="${item.item_id}"
                   onchange="updateTotal(); syncSelectAll();">

            <img src="/static/img/${item.image_path}" alt="${item.name}">

            <div class="cart-item-info">
                <div class="cart-item-title">${item.name}</div>
                <div class="cart-item-price">單價：${item.price}</div>
                <div class="cart-item-price">
                    小計：<span id="subtotal-${item.item_id}">
                        ${item.price * item.quantity}
                    </span>
                </div>
            </div>

            <div class="cart-qty-control">
                <button onclick="changeQty(${item.item_id}, -1)">－</button>
                <input type="text" id="qty-${item.item_id}" value="${item.quantity}">
                <button onclick="changeQty(${item.item_id}, 1)">＋</button>
            </div>

            <button onclick="removeItem(${item.item_id})"
                    style="background:#d9534f;">
                移除
            </button>
        `;

        container.appendChild(div);

        // ⭐ 綁定手動輸入檢查
        const input = div.querySelector(`#qty-${item.item_id}`);
        input.addEventListener("input", () => validateQty(item.item_id));
    });

    updateTotal();
    syncSelectAll();
}

// ================================
// 修改數量（按鈕版，自動修正庫存上限）
// ================================
async function changeQty(itemId, delta) {
    const input = document.getElementById(`qty-${itemId}`);
    let value = parseInt(input.value, 10) || 1;

    const item = cartData.find(i => i.item_id === itemId);
    if (!item) return;

    value += delta;

    // 下限
    if (value < 1) value = 1;

    // 上限
    if (typeof item.stock === "number" && value > item.stock) {
        value = item.stock;
    }

    input.value = value;

    // 更新小計
    document.getElementById(`subtotal-${itemId}`).textContent =
        item.price * value;

    // 同步後端
    await fetch("/api/cart/update_quantity", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ item_id: itemId, quantity: value })
    });

    updateTotal();
}

// ================================
// 手動輸入檢查（自動修正庫存上限）
// ================================
async function validateQty(itemId) {
    const input = document.getElementById(`qty-${itemId}`);
    let value = parseInt(input.value, 10) || 1;

    const item = cartData.find(i => i.item_id === itemId);
    if (!item) return;

    // 下限
    if (value < 1) value = 1;

    // 上限
    if (typeof item.stock === "number" && value > item.stock) {
        value = item.stock;
    }

    input.value = value;

    // 更新小計
    document.getElementById(`subtotal-${itemId}`).textContent =
        item.price * value;

    // 同步後端
    await fetch("/api/cart/update_quantity", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ item_id: itemId, quantity: value })
    });

    updateTotal();
}

// ================================
// 更新總金額
// ================================
function updateTotal() {
    const checks = document.querySelectorAll(".cart-check");
    let total = 0;

    checks.forEach((chk, index) => {
        if (chk.checked) {
            const item = cartData[index];
            const qty = parseInt(
                document.getElementById(`qty-${item.item_id}`).value
            );
            total += item.price * qty;
        }
    });

    document.getElementById("cartTotal").textContent = `總金額：${total}`;
}

// ================================
// 全選
// ================================
function toggleSelectAll(all) {
    const checks = document.querySelectorAll(".cart-check");
    checks.forEach(c => c.checked = all.checked);
    updateTotal();
}

// ================================
// 單選同步全選
// ================================
function syncSelectAll() {
    const checks = document.querySelectorAll(".cart-check");
    const selectAll = document.getElementById("selectAll");
    if (!selectAll) return;

    selectAll.checked =
        checks.length > 0 && [...checks].every(c => c.checked);
}

// ================================
// 移除商品
// ================================
async function removeItem(itemId) {
    const res = await fetch("/api/cart/remove", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ item_id: itemId })
    });

    const data = await res.json();
    if (data.message) alert(data.message);

    loadCart();
}

// ================================
// 結帳
// ================================
async function checkout() {
    const checkedItems = [...document.querySelectorAll(".cart-check:checked")]
        .map(chk => chk.dataset.itemId);

    if (checkedItems.length === 0) {
        alert("請至少選擇一項商品");
        return;
    }

    const res = await fetch("/api/cart/checkout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ items: checkedItems })
    });

    const data = await res.json();

    if (data.error) {
        alert(data.error);
        return;
    }

    alert("結帳完成！");

    // 更新餘額
    if (data.new_money !== undefined) {
        document.getElementById("user-money").textContent = data.new_money;
    }

    document.getElementById("cartTotal").textContent = "總金額：0";
    const selectAll = document.getElementById("selectAll");
    if (selectAll) selectAll.checked = false;

    loadCart();
}
