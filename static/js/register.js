function updateStats() {
    const strength = parseInt(regStrength.value);
    const intelligence = parseInt(regIntelligence.value);
    const luck = parseInt(regLuck.value);

    const total = strength + intelligence + luck;
    const left = 30 - total;

    // 更新顯示
    strengthValue.textContent = strength;
    intelligenceValue.textContent = intelligence;
    luckValue.textContent = luck;
    pointsLeft.textContent = left;

    // 顏色變化
    if (left < 0) {
        pointsLeft.style.color = "red";
    } else {
        pointsLeft.style.color = "green";
    }
}

// 綁定 slider 事件
regStrength.addEventListener("input", updateStats);
regIntelligence.addEventListener("input", updateStats);
regLuck.addEventListener("input", updateStats);

// 初始化
updateStats();


// ================================
// 註冊按鈕
// ================================
document.getElementById("registerBtn").addEventListener("click", async () => {
    const account = regAccount.value;
    const name = regName.value;
    const password = regPassword.value;

    const strength = parseInt(regStrength.value);
    const intelligence = parseInt(regIntelligence.value);
    const luck = parseInt(regLuck.value);

    if (!account || !name || !password) {
        alert("請完整輸入帳號、名字和密碼！");
        return;
    }

    if (strength + intelligence + luck > 30) {
        alert("能力點數總和不能超過 30 點！");
        return;
    }

    try {
        const res = await fetch("/api/register", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                account,
                name,
                password,
                strength,
                intelligence,
                luck
            })
        });

        const data = await res.json();
        alert(data.message);

        if (data.status === "success") {
            window.location.href = "/login";
        }
    } catch (err) {
        console.error("註冊失敗:", err);
        alert("系統錯誤，請稍後再試！");
    }
});
