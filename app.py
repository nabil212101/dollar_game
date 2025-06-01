from flask import Flask, request, jsonify, render_template
import sqlite3
from datetime import datetime, timedelta
import os

app = Flask(__name__)

conn = sqlite3.connect('game.db', check_same_thread=False)
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 0,
    last_claim TEXT
)""")
conn.commit()

def get_user(user_id):
    c.execute("SELECT balance, last_claim FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    if not row:
        c.execute("INSERT INTO users (user_id, balance, last_claim) VALUES (?, ?, ?)",
                  (user_id, 0, '1970-01-01T00:00:00'))
        conn.commit()
        return 0, datetime(1970, 1, 1)
    balance, last_claim = row
    return balance, datetime.fromisoformat(last_claim)

@app.route("/game")
def game():
    return render_template("game.html")

@app.route("/api/status")
def status():
    user_id = int(request.args.get("user_id"))
    balance, last_claim = get_user(user_id)
    now = datetime.now()
    can_claim = now - last_claim >= timedelta(minutes=5)  # اللعب كل 5 دقائق
    return jsonify({"balance": balance, "can_claim": can_claim})

@app.route("/api/claim", methods=["POST"])
def claim():
    user_id = int(request.args.get("user_id"))
    balance, last_claim = get_user(user_id)
    now = datetime.now()
    if now - last_claim < timedelta(minutes=5):
        remaining = timedelta(minutes=5) - (now - last_claim)
        seconds = int(remaining.total_seconds())
        minutes = seconds // 60
        seconds = seconds % 60
        return jsonify({"message": f"يجب الانتظار {minutes} دقيقة و {seconds} ثانية قبل المحاولة مرة أخرى!"})
    new_balance = balance + 1
    c.execute("UPDATE users SET balance=?, last_claim=? WHERE user_id=?",
              (new_balance, now.isoformat(), user_id))
    conn.commit()
    return jsonify({"message": "تم إضافة دولار إلى رصيدك!"})

# إضافة هذا المسار لتسجيل المستخدم عند تسجيل الدخول بتليغرام
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    user_id = data.get("id")
    if not user_id:
        return jsonify({"error": "user_id مطلوب"}), 400
    # تحقق من وجود المستخدم، وإذا لم يكن موجودًا يتم إضافته
    c.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
    if not c.fetchone():
        c.execute("INSERT INTO users (user_id, balance, last_claim) VALUES (?, ?, ?)",
                  (user_id, 0, '1970-01-01T00:00:00'))
        conn.commit()
    return jsonify({"message": "تم تسجيل الدخول بنجاح!"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
