from flask import Flask, render_template, request, redirect, session, g, url_for, send_from_directory
import os
import sqlite3
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "your_secret_key"
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

DATABASE = "database.db"

# Ensure upload directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        existing_user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if existing_user:
            return "User already exists"

        db.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        db.commit()
        return redirect("/login")
    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password)).fetchone()
        if user:
            session["user_id"] = user["id"]
            return redirect("/dashboard")
        else:
            return "Invalid credentials"
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    db = get_db()
    user_id = session["user_id"]

    if request.method == "POST":
        year = request.form["year"]
        category = request.form["category"]
        sport = request.form["sport"]
        event = request.form["event"]
        file = request.files["file"]

        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)

            db.execute(
                "INSERT INTO certificates (user_id, year, category, sport, event, filename) VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, year, category, sport, event, filename),
            )
            db.commit()
            return redirect("/dashboard")

    filters = {
        "year": request.args.get("year", ""),
        "category": request.args.get("category", ""),
        "sport": request.args.get("sport", ""),
        "event": request.args.get("event", "")
    }

    query = "SELECT * FROM certificates WHERE user_id = ?"
    params = [user_id]

    for key, value in filters.items():
        if value:
            query += f" AND {key} LIKE ?"
            params.append(f"%{value}%")

    query += " ORDER BY id DESC"
    records = db.execute(query, params).fetchall()

    return render_template("dashboard.html", records=records)
@app.route("/edit/<int:cert_id>", methods=["GET", "POST"])
def edit_certificate(cert_id):
    if "user_id" not in session:
        return redirect("/login")

    db = get_db()

    if request.method == "POST":
        year = request.form["year"]
        category = request.form["category"]
        sport = request.form["sport"]
        event = request.form["event"]

        db.execute(
            "UPDATE certificates SET year = ?, category = ?, sport = ?, event = ? WHERE id = ?",
            (year, category, sport, event, cert_id)
        )
        db.commit()
        return redirect("/dashboard")

    cert = db.execute("SELECT * FROM certificates WHERE id = ?", (cert_id,)).fetchone()
    if cert is None:
        return "Certificate not found", 404

    return render_template("edit_certificate.html", cert=cert)



@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.route("/delete/<int:cert_id>")
def delete_certificate(cert_id):
    if "user_id" not in session:
        return redirect("/login")

    db = get_db()
    cert = db.execute("SELECT * FROM certificates WHERE id = ?", (cert_id,)).fetchone()

    if cert and cert["user_id"] == session["user_id"]:
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], cert["filename"])
        if os.path.exists(file_path):
            os.remove(file_path)
        db.execute("DELETE FROM certificates WHERE id = ?", (cert_id,))
        db.commit()

    return redirect("/dashboard")


if __name__ == "__main__":
    app.run(debug=True)
