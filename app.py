"""Recall Radar - a forgetting-curve tracker. Flask + MySQL CRUD app.

Run:
    pip install -r requirements.txt
    mysql -u root -p < schema.sql
    export DB_USER=root DB_PASSWORD=yourpass   # optional: DB_HOST, DB_NAME
    python app.py   ->  http://127.0.0.1:5000
"""
import os
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-me")


def get_db():
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        user=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASSWORD", ""),
        database=os.environ.get("DB_NAME", "recall_radar"),
    )


def query(sql, params=(), commit=False):
    conn = get_db()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params)
        if commit:
            conn.commit()
            return cur.lastrowid
        return cur.fetchall()
    finally:
        conn.close()


# ---- The "few SQL queries" ----------------------------------------------

# 1. Everything, weakest memory first
Q_ALL = "SELECT * FROM topic_retention ORDER BY retention ASC"

# 2. Fading: topics you should revisit now (retention under 60%)
Q_DUE = "SELECT * FROM topic_retention WHERE retention < 60 ORDER BY retention ASC LIMIT 5"

# 3. Category health: average retention and topic counts per category
Q_CATEGORY = """
    SELECT category, COUNT(*) AS topics, ROUND(AVG(retention), 1) AS avg_retention,
           SUM(retention < 60) AS fading
    FROM topic_retention GROUP BY category ORDER BY avg_retention ASC
"""

# 4. Study streak: reviews logged per day over the last 7 days
Q_STREAK = """
    SELECT DATE(reviewed_at) AS day, COUNT(*) AS reviews, ROUND(AVG(confidence), 1) AS avg_conf
    FROM reviews WHERE reviewed_at >= NOW() - INTERVAL 7 DAY
    GROUP BY DATE(reviewed_at) ORDER BY day DESC
"""

# 5. Confidence trend per topic: first vs latest review (are you actually improving?)
Q_TREND = """
    SELECT t.name,
           (SELECT confidence FROM reviews WHERE topic_id = t.id ORDER BY reviewed_at ASC  LIMIT 1) AS first_conf,
           (SELECT confidence FROM reviews WHERE topic_id = t.id ORDER BY reviewed_at DESC LIMIT 1) AS latest_conf
    FROM topics t
    HAVING first_conf IS NOT NULL AND latest_conf <> first_conf
    ORDER BY (latest_conf - first_conf) DESC LIMIT 5
"""


@app.route("/")
def index():
    return render_template(
        "index.html",
        topics=query(Q_ALL),
        due=query(Q_DUE),
        categories=query(Q_CATEGORY),
        streak=query(Q_STREAK),
        trend=query(Q_TREND),
    )


@app.post("/topics")
def create_topic():
    name = request.form["name"].strip()
    if not name:
        flash("Topic name is required.")
        return redirect(url_for("index"))
    query(
        "INSERT INTO topics (name, category, difficulty) VALUES (%s, %s, %s)",
        (name, request.form.get("category", "General").strip() or "General",
         int(request.form.get("difficulty", 3))),
        commit=True,
    )
    return redirect(url_for("index"))


@app.post("/topics/<int:topic_id>/edit")
def update_topic(topic_id):
    query(
        "UPDATE topics SET name=%s, category=%s, difficulty=%s WHERE id=%s",
        (request.form["name"].strip(), request.form["category"].strip(),
         int(request.form["difficulty"]), topic_id),
        commit=True,
    )
    return redirect(url_for("index"))


@app.post("/topics/<int:topic_id>/delete")
def delete_topic(topic_id):
    query("DELETE FROM topics WHERE id=%s", (topic_id,), commit=True)  # reviews cascade
    return redirect(url_for("index"))


@app.post("/topics/<int:topic_id>/review")
def add_review(topic_id):
    query(
        "INSERT INTO reviews (topic_id, confidence, notes) VALUES (%s, %s, %s)",
        (topic_id, int(request.form["confidence"]), request.form.get("notes", "")[:255]),
        commit=True,
    )
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
