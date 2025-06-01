<!DOCTYPE html>
<html lang="ar">
<head>
    <meta charset="UTF-8">
    <title>لعبة الدولار كل 5 دقائق</title>
    <link rel="icon" href="{{ url_for('static', filename='favicon.ico') }}">
    <style>
        body {
            direction: rtl;
            font-family: Arial, sans-serif;
            background-color: #f0f2f5;
            text-align: center;
            padding: 50px;
        }
        #container {
            background-color: white;
            border-radius: 10px;
            padding: 30px;
            display: inline-block;
            box-shadow: 0 0 15px rgba(0,0,0,0.1);
        }
        input, button {
            padding: 10px;
            font-size: 16px;
            margin: 10px;
        }
    </style>
</head>
<body>
    <div id="container">
        <h1>💰 لعبة ربح دولار كل 5 دقائق</h1>

        <!-- Telegram Login Widget -->
        <div id="login-section">
            <script async src="https://telegram.org/js/telegram-widget.js?7"
                data-telegram-login="giparty_bot"
                data-size="large"
                data-userpic="false"
                data-request-access="write"
                data-lang="ar"
                data-on-auth="onTelegramAuth">
            </script>
        </div>

        <div id="game-section" style="display:none;">
            <p>رصيدك الحالي: <span id="balance">0</span> 💵</p>
            <p id="status"></p>
            <button id="claimBtn" onclick="claim()">احصل على دولار</button>
        </div>
    </div>

    <script>
        let userId = null;

        function onTelegramAuth(user) {
            userId = user.id;

            fetch("/api/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ id: user.id, username: user.username })
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById("login-section").style.display = "none";
                document.getElementById("game-section").style.display = "block";
                checkStatus();
            })
            .catch(error => {
                alert("حدث خطأ في تسجيل الدخول: " + error.message);
            });
        }

        function checkStatus() {
            fetch(`/api/status?user_id=${userId}`)
            .then(response => response.json())
            .then(data => {
                document.getElementById("balance").innerText = data.balance;
                document.getElementById("claimBtn").disabled = !data.can_claim;
                document.getElementById("status").innerText = data.can_claim
                    ? "يمكنك المطالبة الآن ✅"
                    : "لا يمكنك المطالبة الآن، انتظر 5 دقائق ⏳";
            });
        }

        function claim() {
            fetch(`/api/claim?user_id=${userId}`, {
                method: "POST"
            })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                checkStatus();
            });
        }
    </script>
</body>
</html>
