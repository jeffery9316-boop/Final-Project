const grid = document.getElementById("inventoryGrid");
const tooltip = document.getElementById("item-tooltip");

// Modal 元件
const modal = document.getElementById("itemModal");
const modalClose = document.getElementById("modalClose");
const modalImg = document.getElementById("modalItemImg");
const modalName = document.getElementById("modalItemName");
const modalDesc = document.getElementById("modalItemDesc");
const modalQty = document.getElementById("modalItemQty");
const useQtyText = document.getElementById("useQty");
const qtyPlus = document.getElementById("qtyPlus");
const qtyMinus = document.getElementById("qtyMinus");
const useItemBtn = document.getElementById("useItemBtn");

let currentItem = null;
let currentQty = 1;

// 1️⃣ 載入包包資料
async function loadInventory() {
    const res = await fetch("/api/inventory");
    const items = await res.json();

    grid.innerHTML = ""; // 清空

    items.forEach(item => {
        const slot = document.createElement("div");
        slot.className = "item-slot";

        slot.dataset.name = item.name;
        slot.dataset.desc = item.effect_description;
        slot.dataset.str = item.strength_bonus;
        slot.dataset.int = item.intelligence_bonus;
        slot.dataset.luck = item.luck_bonus;
        slot.dataset.item = JSON.stringify(item);

        slot.innerHTML = `
            <img src="/static/img/${item.image_path}">
            <span class="item-qty">${item.quantity}</span>
        `;

        // 點擊 → 開啟彈窗
        slot.addEventListener("click", () => {
            openItemModal(item);
        });

        grid.appendChild(slot);
    });

    bindTooltipEvents();
}

// 2️⃣ Tooltip 綁定
function bindTooltipEvents() {
    document.querySelectorAll(".item-slot").forEach(slot => {
        slot.addEventListener("mouseenter", () => {
            tooltip.innerHTML = `
                <strong>${slot.dataset.name}</strong><br>
                ${slot.dataset.desc}<br><br>
                <small>
                    力量 +${slot.dataset.str}　
                    智慧 +${slot.dataset.int}　
                    運氣 +${slot.dataset.luck}
                </small>
            `;
            tooltip.style.display = "block";
        });

        slot.addEventListener("mousemove", e => {
            tooltip.style.left = e.pageX + 15 + "px";
            tooltip.style.top = e.pageY + 15 + "px";
        });

        slot.addEventListener("mouseleave", () => {
            tooltip.style.display = "none";
        });
    });
}

// 3️⃣ 開啟彈窗
function openItemModal(item) {
    currentItem = item;
    currentQty = 1;

    modalImg.src = "/static/img/" + item.image_path;
    modalName.textContent = item.name;
    modalDesc.textContent = item.effect_description;
    modalQty.textContent = item.quantity;
    useQtyText.textContent = currentQty;

    modal.style.display = "block";
}

// 4️⃣ 關閉彈窗
modalClose.onclick = () => modal.style.display = "none";
window.onclick = e => { if (e.target === modal) modal.style.display = "none"; };

// 5️⃣ 數量調整
qtyPlus.onclick = () => {
    if (currentQty < currentItem.quantity) {
        currentQty++;
        useQtyText.textContent = currentQty;
    }
};

qtyMinus.onclick = () => {
    if (currentQty > 1) {
        currentQty--;
        useQtyText.textContent = currentQty;
    }
};

// 6️⃣ 使用道具
useItemBtn.onclick = async () => {
    const res = await fetch("/api/use_item", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            item_id: currentItem.item_id,
            quantity: currentQty
        })
    });

    const data = await res.json();

    if (data.error) {
        alert(data.error);
        return;
    }

    alert("使用成功");

    // 1️⃣ 更新能力值動畫
    if (data.stats) {
        animateStats(data.stats);
    }

    // 2️⃣ 重新載入包包（等待完成）
    await loadInventory();

    // 3️⃣ 關閉彈窗
    modal.style.display = "none";
};



// 7️⃣ 能力值動畫
function animateStats(stats) {
    const fields = [
        { id: "stat-strength", value: stats.strength },
        { id: "stat-intelligence", value: stats.intelligence },
        { id: "stat-luck", value: stats.luck }
    ];

    fields.forEach(f => {
        const el = document.getElementById(f.id);
        el.textContent = f.value;

        el.classList.add("stat-animate");
        setTimeout(() => el.classList.remove("stat-animate"), 600);
    });
}

// 初始化
loadInventory();
