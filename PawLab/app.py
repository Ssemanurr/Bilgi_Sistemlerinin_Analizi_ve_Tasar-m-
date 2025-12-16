import json
import os
from flask import Flask, render_template, request, redirect, flash, url_for, session

app = Flask(__name__)
app.secret_key = "pawlab-secret-key"

# ------------------ DOSYA YOLLARI ------------------
APPOINTMENTS_FILE = "data/appointments.json"
USERS_FILE = "data/users.json"
ADMINS_FILE = "data/admins.json"


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
    if "user_email" not in session:
        flash("Randevu almak için giriş yapmalısınız 🔐", "error")
        return redirect(url_for("login"))

    if request.method == "POST":
        appointments = load_json(APPOINTMENTS_FILE)

        new_appointment = {
            "owner": request.form.get("owner"),
            "pet_name": request.form.get("pet_name"),
            "pet_type": request.form.get("pet_type"),
            "date": request.form.get("date"),
            "time": request.form.get("time"),
            "note": request.form.get("note"),
            "status": "beklemede",
            "user_email": session["user_email"]
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
                session["user_email"] = email
                session["user_name"] = user["name"]

                flash("Giriş başarılı ✅", "success")
                return redirect(url_for("appointment"))

        flash("E-posta veya şifre hatalı ❌", "error")

    return render_template("login.html")


# ------------------ ÇIKIŞ ------------------
@app.route("/logout")
def logout():
    session.clear()
    flash("Çıkış yapıldı 👋", "success")
    return redirect(url_for("index"))


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
    if "user_email" not in session:
        flash("Lütfen giriş yapın 🔐", "error")
        return redirect(url_for("login"))

    appointments = load_json(APPOINTMENTS_FILE)
    user_appointments = [
        a for a in appointments if a.get("user_email") == session["user_email"]
    ]

    return render_template("my_appointments.html", appointments=user_appointments)


# ------------------ RANDEVU İPTAL ------------------
@app.route("/cancel-appointment/<int:index>")
def cancel_appointment(index):
    if "user_email" not in session:
        flash("Yetkisiz işlem ❌", "error")
        return redirect(url_for("login"))

    appointments = load_json(APPOINTMENTS_FILE)

    if 0 <= index < len(appointments):
        if appointments[index]["user_email"] == session["user_email"]:
            appointments.pop(index)
            save_json(APPOINTMENTS_FILE, appointments)
            flash("Randevu iptal edildi ❌", "success")

    return redirect(url_for("my_appointments"))


# ------------------ ADMIN GİRİŞ ------------------
@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")

        admins = load_json(ADMINS_FILE)

        for admin in admins:
            if (
                admin["email"] == email and
                admin["username"] == username and
                admin["password"] == password
            ):
                session["admin"] = True
                flash("Yönetici girişi başarılı ✅", "success")
                return redirect(url_for("admin_panel"))

        flash("Yetkisiz giriş ❌", "error")

    return render_template("admin_login.html")


# ------------------ ADMIN PANEL ------------------
@app.route("/admin-panel")
def admin_panel():
    if not session.get("admin"):
        flash("Yetkisiz erişim ❌", "error")
        return redirect(url_for("admin_login"))

    appointments = load_json(APPOINTMENTS_FILE)
    return render_template("admin_panel.html", appointments=appointments)


# ------------------ ÇALIŞTIR ------------------
if __name__ == "__main__":
    app.run(debug=True)

