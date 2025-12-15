import json
import os
from flask import Flask, render_template, request, redirect, flash, url_for

app = Flask(__name__)
app.secret_key = "pawlab-secret-key"

# ------------------ DOSYA YOLLARI ------------------
APPOINTMENTS_FILE = "data/appointments.json"
USERS_FILE = "data/users.json"


# ------------------ YARDIMCI FONKSİYONLAR ------------------
def load_json(path):
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ------------------ ANA SAYFA ------------------
@app.route("/")
def index():
    return render_template("index.html")


# ------------------ RANDEVU AL ------------------
@app.route("/appointment", methods=["GET", "POST"])
def appointment():
    if request.method == "POST":
        appointments = load_json(APPOINTMENTS_FILE)

        new_appointment = {
            "owner": request.form.get("owner"),
            "pet_name": request.form.get("pet_name"),
            "pet_type": request.form.get("pet_type"),
            "date": request.form.get("date"),
            "time": request.form.get("time"),
            "note": request.form.get("note"),
            "status": "beklemede"
        }

        appointments.append(new_appointment)
        save_json(APPOINTMENTS_FILE, appointments)

        flash("Randevunuz başarıyla oluşturuldu ✅", "success")
        return redirect(url_for("appointment"))

    return render_template("appointment.html")


# ------------------ GİRİŞ YAP ------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        users = load_json(USERS_FILE)

        for user in users:
            if user["email"] == email and user["password"] == password:
                flash("Giriş başarılı ✅", "success")
                return redirect(url_for("appointment"))

        flash("E-posta veya şifre hatalı ❌", "error")

    return render_template("login.html")


# ------------------ KAYIT OL ------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        users = load_json(USERS_FILE)

        new_user = {
            "name": request.form.get("name"),
            "email": request.form.get("email"),
            "phone": request.form.get("phone"),
            "password": request.form.get("password")
        }

        users.append(new_user)
        save_json(USERS_FILE, users)

        return render_template("register_success.html")

    return render_template("register.html")


# ------------------ BENİM RANDEVULARIM ------------------
@app.route("/my-appointments")
def my_appointments():
    appointments = load_json(APPOINTMENTS_FILE)
    return render_template("my_appointments.html", appointments=appointments)


# ------------------ ADMIN ------------------
@app.route("/admin")
def admin_login():
    return render_template("admin_login.html")


@app.route("/admin-panel")
def admin_panel():
    appointments = load_json(APPOINTMENTS_FILE)
    return render_template("admin_panel.html", appointments=appointments)


# ------------------ ÇALIŞTIR ------------------
if __name__ == "__main__":
    app.run(debug=True)
