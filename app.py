from flask import Flask, request, jsonify, render_template
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)

# قاعدة البيانات
conn = sqlite3.connect('game.db', check_same_thread=False)
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 0,
    last_claim TEXT
)""")
conn.commit()

# دالة استرجاع بيانات المستخدم
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
    can_claim = now - last_claim >= timedelta(days=1)
    return jsonify({"balance": balance, "can_claim": can_claim})

@app.route("/api/claim", methods=["POST"])
def claim():
    user_id = int(request.args.get("user_id"))
    balance, last_claim = get_user(user_id)
    now = datetime.now()
    if now - last_claim < timedelta(days=1):
        return jsonify({"message": "لقد حصلت على دولار بالفعل اليوم!"})
    new_balance = balance + 1
    c.execute("UPDATE users SET balance=?, last_claim=? WHERE user_id=?",
              (new_balance, now.isoformat(), user_id))
    conn.commit()
    return jsonify({"message": "تم إضافة دولار إلى رصيدك!"})

if __name__ == "__main__":
    app.run(debug=True)
