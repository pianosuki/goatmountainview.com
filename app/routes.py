from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user
from app import app, bcrypt
from app.models import User


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/portfolio")
def portfolio():
    return render_template("portfolio.html")


@app.route("/goats")
def goats():
    return render_template("goats.html")


@app.route("/goats/does")
def does():
    return render_template("does.html")


@app.route("/goats/adoptions")
def adoptions():
    return render_template("adoptions.html")


@app.route("/goats/foundation")
def foundation():
    return render_template("foundation.html")


@app.route("/soap")
def soap():
    return render_template("soap.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash("Success: You have logged in", "success")
            return redirect(url_for("admin"))
        else:
            flash("Error: Invalid credentials", "error")
            return redirect(url_for("login"))
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Info: You have been logged out", "info")
    return redirect("/")


@app.route("/admin")
@login_required
def admin():
    return render_template("admin.html")
