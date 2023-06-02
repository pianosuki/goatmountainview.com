import os
from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user
from werkzeug.utils import secure_filename
from app import app, db, bcrypt
from app.models import User, Soap
from app.crud import get_all_tables, add_table_row, edit_table_row, delete_table_row, get_table_rows
from app.utils import allowed_file


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
    soaps = Soap.query.all()
    return render_template("soap.html", soaps=soaps)


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


@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin():
    if request.method == "POST":
        action = request.form.get("action")
        match action:
            case "edit":
                table_name = request.form["table_name"]
                return redirect(url_for("admin_table", table_name=table_name))
            case "cancel":
                return redirect(url_for("index"))
    tables = get_all_tables().keys()
    return render_template("admin.html", tables=tables)


@app.route("/admin/<table_name>", methods=["GET", "POST"])
@login_required
def admin_table(table_name):
    if request.method == "POST":
        action = request.form.get("action")
        match action:
            case "add":
                column_data = {}
                if "image" in request.files:
                    image = request.files["image"]
                    if image.filename == "":
                        flash("Error: No selected file", "error")
                        return redirect(url_for("admin_table", table_name=table_name))
                    if image and allowed_file(image.filename):
                        filename = secure_filename(image.filename)
                        image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                        add_table_row("images", {"filename": filename})
                        column_data["image"] = filename
                for key, value in request.form.items():
                    match key:
                        case "action":
                            continue
                        case "password":
                            column_data[key] = bcrypt.generate_password_hash(value).decode("utf-8")
                        case _:
                            column_data[key] = value
                add_table_row(table_name, column_data)
                flash(f"Success: Added row ({len(get_table_rows(table_name))}) to table '{table_name}'", "success")
                return redirect(url_for("admin_table", table_name=table_name))
            case "edit":
                row_id = request.form.get("row_id")
                return redirect(url_for("admin_edit", table_name=table_name, row_id=row_id))
            case "delete":
                row_id = request.form.get("row_id")
                delete_table_row(table_name, row_id)
                flash(f"Success: Deleted row ({row_id}) from table '{table_name}'", "success")
            case "cancel":
                return redirect(url_for("admin"))
    table = get_all_tables()[table_name]
    return render_template("admin_table.html", table_name=table_name, table=table)


@app.route("/admin/<table_name>/edit/<row_id>", methods=["GET", "POST"])
@login_required
def admin_edit(table_name, row_id):
    try:
        row_id = int(row_id)
    except ValueError:
        flash("Error: ID must be integer", "error")
        return redirect(url_for("admin_table", table_name=table_name))
    if request.method == "POST":
        action = request.form.get("action")
        match action:
            case "edit":
                column_data = {}
                if "image" in request.files:
                    image = request.files["image"]
                    if image and allowed_file(image.filename):
                        filename = secure_filename(image.filename)
                        image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                        add_table_row("images", {"filename": filename})
                        column_data["image"] = filename
                for key, value in request.form.items():
                    match key:
                        case "action":
                            continue
                        case "password":
                            column_data[key] = bcrypt.generate_password_hash(value).decode("utf-8")
                        case _:
                            column_data[key] = value
                edit_table_row(table_name, row_id, column_data)
                flash(f"Success: Edited row ({row_id}) in table '{table_name}'", "success")
                return redirect(url_for("admin_table", table_name=table_name))
            case "cancel":
                return redirect(url_for("admin_table", table_name=table_name))
    table = get_all_tables()[table_name]
    return render_template("admin_edit.html", table_name=table_name, table=table, row_id=row_id)
