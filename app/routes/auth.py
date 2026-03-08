"""
Auth Routes

Authentication routes (login/logout).
"""

from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user
from app import app, bcrypt
from app.models import User


@app.route("/login", methods=["GET", "POST"])
def login():
    """Login page."""
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


@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    """Logout and redirect to homepage."""
    logout_user()
    flash("Info: You have been logged out", "info")
    return redirect("/")
