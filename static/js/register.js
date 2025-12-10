document.getElementById("registerBtn").addEventListener("click", async () => {
    const account = document.getElementById("regAccount").value;
    const name = document.getElementById("regName").value;
    const password = document.getElementById("regPassword").value;

    if (!account || !name || !password) {
        alert("請完整輸入帳號、名字和密碼！");
        return;
    }

    try {
        const res = await fetch("/api/register", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ account, name, password })
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