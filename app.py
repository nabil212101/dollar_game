import flask
print("Flask version:", flask.__version__)

from flask import Flask, request, jsonify, render_template, g
import sqlite3
from datetime import datetime, timedelta
import os

app = Flask(__name__)
DATABASE = 'game.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    db = sqlite3.connect(DATABASE)  # هنا فتح اتصال مستقل لتهيئة القاعدة
    c = db.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        balance INTEGER DEFAULT 0,
        last_claim TEXT
    )""")
    db.commit()
    db.close()

def get_user(user_id):
    db = get_db()
    c = db.cursor()
    c.execute("SELECT balance, last_claim FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    if not row:
        c.execute("INSERT INTO users (user_id, balance, last_claim) VALUES (?, ?, ?)",
                  (user_id, 0, '1970-01-01T00:00:00'))
        db.commit()
        return 0, datetime(1970, 1, 1)
    balance, last_claim = row
    return balance, datetime.fromisoformat(last_claim)

@app.route("/")
def home():
    return render_template("game.html")

@app.route("/game")
def game():
    return render_template("game.html")

@app.route("/api/status")
def status():
    user_id = request.args.get("user_id")
    if not user_id or not user_id.isdigit():
        return jsonify({"error": "user_id غير صالح"}), 400
    user_id = int(user_id)
    balance, last_claim = get_user(user_id)
    now = datetime.now()
    can_claim = now - last_claim >= timedelta(minutes=5)
    return jsonify({"balance": balance, "can_claim": can_claim})

@app.route("/api/claim", methods=["POST"])
def claim():
    user_id = request.args.get("user_id")
    if not user_id or not user_id.isdigit():
        return jsonify({"error": "user_id غير صالح"}), 400
    user_id = int(user_id)
    balance, last_claim = get_user(user_id)
    now = datetime.now()
    if now - last_claim < timedelta(minutes=5):
        remaining = timedelta(minutes=5) - (now - last_claim)
        seconds = int(remaining.total_seconds())
        minutes = seconds // 60
        seconds = seconds % 60
        return jsonify({"message": f"يجب الانتظار {minutes} دقيقة و {seconds} ثانية قبل المحاولة مرة أخرى!"})
    new_balance = balance + 1
    db = get_db()
    c = db.cursor()
    c.execute("UPDATE users SET balance=?, last_claim=? WHERE user_id=?",
              (new_balance, now.isoformat(), user_id))
    db.commit()
    return jsonify({"message": "تم إضافة دولار إلى رصيدك!"})

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    user_id = data.get("id")
    if not user_id or not isinstance(user_id, int):
        return jsonify({"error": "user_id مطلوب ويجب أن يكون عددًا صحيحًا"}), 400
    db = get_db()
    c = db.cursor()
    c.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
    if not c.fetchone():
        c.execute("INSERT INTO users (user_id, balance, last_claim) VALUES (?, ?, ?)",
                  (user_id, 0, '1970-01-01T00:00:00'))
        db.commit()
    return jsonify({"message": "تم تسجيل الدخول بنجاح!"})

if __name__ == "__main__":
    init_db()  # تهيئة قاعدة البيانات عند بدء التطبيق مباشرة
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
