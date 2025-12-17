const grid = document.getElementById("inventoryGrid");
const tooltip = document.getElementById("item-tooltip");

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

        slot.innerHTML = `
            <img src="/static/img/${item.image_path}">
            <span class="item-qty">${item.quantity}</span>
        `;

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

// 初始化
loadInventory();
