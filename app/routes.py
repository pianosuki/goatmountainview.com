import os

import sqlalchemy.exc
from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user
from werkzeug.utils import secure_filename
from app import app, bcrypt
from app.models import *
from app.utils import allowed_file, total_images_width
import app.crud as crud


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/portfolio")
def portfolio():
    books_table = crud.get_table("books")
    image_folder = app.config["STATIC_FOLDER"] + "/images/books/"
    image_filenames = [filename for filename in os.listdir(image_folder) if os.path.isfile(os.path.join(image_folder, filename))]
    images_width = total_images_width([image_folder + image for image in image_filenames], 200)
    return render_template("portfolio.html", books=books_table, slideshow_images=image_filenames, slideshow_width=images_width)


@app.route("/goats")
def goats():
    return render_template("goats.html")


@app.route("/goats/does")
def does():
    does_list = Doe.query.all()
    image_folder = app.config["UPLOAD_FOLDER"] + "/does"
    image_paths = [f"/uploads/does/{filename}" for filename in os.listdir(image_folder) if os.path.isfile(os.path.join(image_folder, filename))]
    image_filenames = [filename for filename in os.listdir(image_folder) if os.path.isfile(os.path.join(image_folder, filename))]
    images_width = total_images_width([os.path.join(image_folder, image) for image in image_filenames], 200)
    return render_template("does.html", does=does_list, slideshow_images=image_paths, slideshow_width=images_width)


@app.route("/goats/adoptions")
def adoptions():
    image_folder = app.config["UPLOAD_FOLDER"] + "/adoptions"
    image_paths = [f"/uploads/adoptions/{filename}" for filename in os.listdir(image_folder) if os.path.isfile(os.path.join(image_folder, filename))]
    image_filenames = [filename for filename in os.listdir(image_folder) if os.path.isfile(os.path.join(image_folder, filename))]
    images_width = total_images_width([os.path.join(image_folder, image) for image in image_filenames], 200)
    return render_template("adoptions.html", slideshow_images=image_paths, slideshow_width=images_width)


@app.route("/goats/foundation")
def foundation():
    foundation_list = Foundation.query.all()
    image_folder = app.config["UPLOAD_FOLDER"] + "/foundation"
    image_paths = [f"/uploads/foundation/{filename}" for filename in os.listdir(image_folder) if os.path.isfile(os.path.join(image_folder, filename))]
    image_filenames = [filename for filename in os.listdir(image_folder) if os.path.isfile(os.path.join(image_folder, filename))]
    images_width = total_images_width([os.path.join(image_folder, image) for image in image_filenames], 200)
    return render_template("foundation.html", foundation=foundation_list, slideshow_images=image_paths, slideshow_width=images_width)


@app.route("/soap")
def soap():
    soaps_table = Soap.query.all()
    return render_template("soap.html", soaps=soaps_table)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        column_data = {}
        for key, value in request.form.items():
            match key:
                case "action":
                    continue
                case "first_name" | "last_name":
                    column_data[key] = value.strip().lower().capitalize()
                case _:
                    column_data[key] = value.strip()
        crud.add_table_row("inquiries", column_data)
        flash(f"Success: Your inquiry has been sent", "success")
        return redirect(url_for("contact"))
    else:
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
    tables = list(crud.get_all_tables().keys())
    return render_template("admin.html", tables=tables)


@app.route("/admin/<table_name>", methods=["GET", "POST"])
@login_required
def admin_table(table_name):
    if request.method == "POST":
        action = request.form.get("action")
        match action:
            case "add":
                column_data = {}
                image_is_uploaded = False
                if "image" in request.files:
                    image = request.files["image"]
                    if image.filename == "":
                        flash("Error: No selected file", "error")
                        return redirect(url_for("admin_table", table_name=table_name))
                    if image and allowed_file(image.filename):
                        filename = secure_filename(image.filename)
                        directory = request.form["directory"] if table_name == "images" else ""
                        file_path = os.path.join(app.config["UPLOAD_FOLDER"], directory, filename)
                        if os.path.exists(file_path):
                            flash(f"Error: Image with filename '{filename}' already exists", "error")
                            return redirect(url_for("admin_table", table_name=table_name))
                        if table_name == "images":
                            os.makedirs(os.path.join(app.config["UPLOAD_FOLDER"], directory), exist_ok=True)
                            column_data["filename"] = filename
                        else:
                            try:
                                crud.add_table_row("images", {"filename": filename})
                                image_id = crud.search_table_row("images", {"filename": filename}).get("id")
                                column_data["image_id"] = image_id
                            except sqlalchemy.exc.IntegrityError:
                                flash(f"Error: Image with filename '{filename}' already exists", "error")
                                return redirect(url_for("admin_table", table_name=table_name))
                        image.save(file_path)
                        flash(f"Info: Uploaded file '{filename}'", "info")
                        image_is_uploaded = True
                for key, value in request.form.items():
                    match key:
                        case "action":
                            continue
                        case "password":
                            column_data[key] = bcrypt.generate_password_hash(value).decode("utf-8")
                        case _:
                            column_data[key] = value
                try:
                    crud.add_table_row(table_name, column_data)
                    flash(f"Success: Added row ({len(crud.get_table_rows(table_name))}) to table '{table_name}'", "success")
                except (IndexError, FileNotFoundError, ValueError) as e:
                    if "image" in request.files and image_is_uploaded:
                        image = request.files["image"]
                        filename = secure_filename(image.filename)
                        directory = request.form["directory"] if table_name == "images" else ""
                        file_path = os.path.join(app.config["UPLOAD_FOLDER"], directory, filename)
                        if os.path.exists(file_path):
                            os.remove(file_path)
                            flash(f"Info: Deleted file '{filename}'", "info")
                        image_row = crud.search_table_row("images", {"filename": filename, "directory": directory})
                        crud.delete_table_row("images", image_row["id"])
                    flash(f"Error: {e}", "error")
                return redirect(url_for("admin_table", table_name=table_name))
            case "edit":
                row_id = int(request.form.get("row_id"))
                return redirect(url_for("admin_edit", table_name=table_name, row_id=row_id))
            case "delete":
                row_id = int(request.form.get("row_id"))
                if table_name == "images":
                    image_row = crud.get_table_row(table_name, row_id)
                    filename = image_row.get("filename")
                    directory = image_row.get("directory")
                    file_path = os.path.join(app.config["UPLOAD_FOLDER"], directory, filename)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        directory_path = os.path.join(app.config["UPLOAD_FOLDER"], directory)
                        if len(os.listdir(directory_path)) == 0:
                            os.rmdir(directory_path)
                            flash(f"Info: Deleted empty directory '{directory}'", "info")
                        flash(f"Info: Deleted file '{filename}'", "info")
                crud.delete_table_row(table_name, row_id)
                flash(f"Success: Deleted row ({row_id}) from table '{table_name}'", "success")
            case "cancel":
                return redirect(url_for("admin"))
    table = crud.get_all_tables()[table_name]
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
                for key, value in request.form.items():
                    match key:
                        case "action":
                            continue
                        case "password":
                            column_data[key] = bcrypt.generate_password_hash(value).decode("utf-8")
                        case _:
                            column_data[key] = value
                if table_name == "images":
                    image_row = crud.get_table_row(table_name, row_id)
                    existing_filename = image_row.get("filename")
                    existing_directory = image_row.get("directory", "")
                    existing_file_path = os.path.join(app.config["UPLOAD_FOLDER"], existing_directory, existing_filename)
                    new_filename = column_data.get("filename", existing_filename)
                    new_directory = column_data.get("directory", existing_directory)
                    new_file_path = os.path.join(app.config["UPLOAD_FOLDER"], new_directory, new_filename)
                    os.makedirs(os.path.join(app.config["UPLOAD_FOLDER"], new_directory), exist_ok=True)
                    os.rename(existing_file_path, new_file_path)
                    flash(f"Info: Renamed file '{os.path.join(existing_directory, existing_filename)}' to '{os.path.join(new_directory, new_filename)}'", "info")
                try:
                    crud.edit_table_row(table_name, row_id, column_data)
                    flash(f"Success: Edited row ({row_id}) in table '{table_name}'", "success")
                except (IndexError, FileNotFoundError, ValueError) as e:
                    flash(f"Error: {e}", "error")
                    return redirect(url_for("admin_table", table_name=table_name))
                return redirect(url_for("admin_table", table_name=table_name))
            case "cancel":
                return redirect(url_for("admin_table", table_name=table_name))
    table = crud.get_all_tables()[table_name]
    return render_template("admin_edit.html", table_name=table_name, table=table, row_id=row_id)
