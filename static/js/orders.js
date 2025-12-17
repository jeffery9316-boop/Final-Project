document.querySelectorAll(".detail-btn").forEach(btn => {
    btn.addEventListener("click", async () => {
        const orderId = btn.dataset.id;
        const box = document.getElementById("details-" + orderId);

        // 如果已經展開 → 收起
        if (box.style.display === "block") {
            box.style.display = "none";
            return;
        }

        // 呼叫 API
        const res = await fetch(`/api/order_details/${orderId}`);
        const details = await res.json();

        // 生成 HTML
        box.innerHTML = `
            <table>
                <tr><th>商品</th><th>數量</th><th>單價</th><th>小計</th></tr>
                ${details.map(d => `
                    <tr>
                        <td>${d.name}</td>
                        <td>${d.quantity}</td>
                        <td>${d.price}</td>
                        <td>${d.quantity * d.price}</td>
                    </tr>
                `).join("")}
            </table>
        `;

        box.style.display = "block";
    });
});
