document.getElementById("loginBtn").addEventListener("click", async () => {

    const account = document.getElementById("loginAccount").value;
    const password = document.getElementById("loginPassword").value;

    if (!account || !password) {
        alert("請輸入帳號和密碼！");
        return;
    }

    try {
        const res = await fetch("/api/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ account, password })
        });

        const data = await res.json();
        alert(data.message);

        if (data.status === "success") {
            // 儲存 user_id 與名字到 localStorage
            localStorage.setItem("user_id", data.user_id);
            localStorage.setItem("user_name", data.name);
            window.location.href = "/shopping";
        }
    } catch (err) {
        console.error("登入失敗:", err);
        alert("系統錯誤，請稍後再試！");
    }
});

