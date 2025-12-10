document.getElementById("loginBtn").addEventListener("click", async () => {

    const account = document.getElementById("loginAccount").value;
    const password = document.getElementById("loginPassword").value;

    const res = await fetch("/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ account, password })
    });

    const data = await res.json();
    alert(data.message);

    if (data.status === "success") {
        // 登入成功後導向到首頁 or 購物頁 (你可自己改)
        window.location.href = "/shopping";
    }
});
