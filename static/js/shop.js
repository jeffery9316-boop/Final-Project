let itemsMap = {};

// ================================
// 讀取全部商品
// ================================
async function loadItems() {
    const res = await fetch("/api/items");
    const items = await res.json();
    renderItems(items);
}

// ================================
// 套用篩選器
// ================================
async function applyFilter() {
    let rarities = [];
    const allCheck = document.getElementById("rarity-all");

    if (!allCheck.checked) {
        const rarityNodes = document.querySelectorAll(".rarity-check:checked");
        rarities = Array.from(rarityNodes).map(c => c.value);
    }

    const strength = document.getElementById("filter-strength").value || 0;
    const intelligence = document.getElementById("filter-intelligence").value || 0;
    const luck = document.getElementById("filter-luck").value || 0;

    const res = await fetch("/api/filter_items", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            rarities,
            strength,
            intelligence,
            luck
        })
    });

    const filteredItems = await res.json();
    renderItems(filteredItems);
}

// ================================
// 渲染商品卡片 (含購物車按鈕)
// ================================
function renderItems(items) {
    const grid = document.getElementById("itemsGrid");
    grid.innerHTML = "";
    itemsMap = {}; // 重建 map

    items.forEach(item => {
        itemsMap[item.item_id] = item; // ★ 記住每個商品
        const card = document.createElement("div");
        card.className = "item-card";

        card.innerHTML = `
            <img src="/static/img/${item.image_path}" alt="${item.name}" class="item-img">

            <h3>${item.name}</h3>
            <p>稀有度：${item.rarity}</p>
            <p>價格：${item.price}</p>
            <p>庫存：${item.stock}</p>

            <p class="item-description">${item.effect_description}</p>

            <div class="item-bonus">
                力量 +${item.strength_bonus}　
                智慧 +${item.intelligence_bonus}　
                運氣 +${item.luck_bonus}
            </div>

            <div class="shop-qty-control">
                <button onclick="changeQty(${item.item_id}, -1)">－</button>
                <input type="text" id="qty-${item.item_id}" value="1">
                <button onclick="changeQty(${item.item_id}, 1)">＋</button>
            </div>

            <button onclick="addToCart(${item.item_id})">加入購物車</button>
        `;

        grid.appendChild(card);

        // ⭐ 綁定手動輸入檢查
        const input = card.querySelector(`#qty-${item.item_id}`);
        input.addEventListener("input", () => validateQty(item.item_id));
    });
}

// ================================
// 加入購物車
// ================================
async function addToCart(itemId) {
    const qty = parseInt(document.getElementById(`qty-${itemId}`).value);
    const userId = localStorage.getItem("user_id");

    if (!userId) {
        alert("請先登入！");
        window.location.href = "/login";
        return;
    }

    const res = await fetch("/api/cart/add", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            user_id: userId,
            item_id: itemId,
            quantity: qty
        })
    });

    const data = await res.json();
    alert(data.message);
}

// ================================
// 數量增減按鈕
// ================================
function changeQty(itemId, delta) {
    const input = document.getElementById(`qty-${itemId}`);
    let value = parseInt(input.value) || 1;

    const item = itemsMap[itemId];
    if (!item) return;

    value += delta;

    // 下限
    if (value < 1) value = 1;

    // 上限（庫存）
    if (value > item.stock) {
        value = item.stock;
    }

    input.value = value;
}

// ================================
// 手動輸入檢查
// ================================
function validateQty(itemId) {
    const input = document.getElementById(`qty-${itemId}`);
    let value = parseInt(input.value, 10) || 1;

    const item = itemsMap[itemId];
    if (!item) return;

    // 下限
    if (value < 1) value = 1;

    // 上限
    if (value > item.stock) {
        value = item.stock;
    }

    input.value = value;
}

// ================================
// 「全部」與個別 checkbox 控制邏輯
// ================================
function setupRarityCheckboxLogic() {
    const allCheck = document.getElementById("rarity-all");
    const rarityChecks = document.querySelectorAll(".rarity-check");

    allCheck.addEventListener("change", () => {
        rarityChecks.forEach(c => c.checked = allCheck.checked);
    });

    rarityChecks.forEach(c => {
        c.addEventListener("change", () => {
            const allSelected = Array.from(rarityChecks).every(x => x.checked);
            allCheck.checked = allSelected;
        });
    });
}

// ================================
// 頁面載入時初始化
// ================================
document.addEventListener("DOMContentLoaded", () => {
    loadItems();
    document.getElementById("filter-btn").addEventListener("click", applyFilter);
    setupRarityCheckboxLogic();
});
