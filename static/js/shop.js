async function loadItems() {
    const res = await fetch("/api/items");
    const items = await res.json();

    const grid = document.getElementById("itemsGrid");
    grid.innerHTML = "";

    items.forEach(item => {
        const card = document.createElement("div");
        card.className = "item-card";

        card.innerHTML = `
            <img src="/static/img/${item.image_path}" alt="${item.name}" class="item-img">
            <h3>${item.name}</h3>
            <p>稀有度：${item.rarity}</p>
            <p>價格：${item.price}</p>
            <p>庫存：${item.stock}</p>
            <p class="item-description">${item.effect_description}</p>
            <div class="qty-control">
                <button onclick="changeQty(${item.item_id}, -1)">－</button>
                <input type="text" id="qty-${item.item_id}" value="1">
                <button onclick="changeQty(${item.item_id}, 1)">＋</button>
            </div>
            
            <button onclick="addToCart(${item.item_id})">加入購物車</button>
        `;

        grid.appendChild(card);
    });
}

async function addToCart(itemId) {
    const qty = document.getElementById(`qty-${itemId}`).value;
    const userId = localStorage.getItem("user_id"); // 從登入時存的 user_id 取出

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
            quantity: parseInt(qty)
        })
    });

    const data = await res.json();
    alert(data.message);
}

function changeQty(itemId, delta) {
    const input = document.getElementById(`qty-${itemId}`);
    let value = parseInt(input.value) || 1;
    value += delta;
    if (value < 1) value = 1;
    input.value = value;
}

document.addEventListener("DOMContentLoaded", loadItems);

