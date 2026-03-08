"""
Admin Routes

Routes for the admin panel (authentication required).
"""

import json
import os
import tempfile
from datetime import datetime

import sqlalchemy.exc
from flask import render_template, redirect, url_for, request, flash, send_file, jsonify
from flask_login import login_required
from werkzeug.utils import secure_filename

import app.crud as crud
from app import app, bcrypt, db
from app.models import *
from app.utils import allowed_file
from app.field_mappings import USER_FIELDS
from app.export_import import export_database, import_database


def get_user_fields_for_table(table_name: str) -> list:
    """Get user-friendly form fields for a table"""
    return USER_FIELDS.get(table_name, [])


def process_column_data(column_data: dict) -> dict:
    """Process column data before saving (handles special conversions)."""
    processed = column_data.copy()
    
    # Handle image_id conversions
    if "image_id" in processed:
        value = processed["image_id"]
        if isinstance(value, str):
            if value:
                try:
                    processed["image_id"] = crud.image_id_from_string(value)
                except (IndexError, FileNotFoundError, ValueError):
                    processed["image_id"] = None
            else:
                processed["image_id"] = None
    
    # Handle goat_id conversions
    if "goat_id" in processed:
        value = processed["goat_id"]
        if isinstance(value, str):
            if value:
                try:
                    processed["goat_id"] = crud.goat_id_from_string(value)
                except (IndexError, ValueError):
                    pass
            else:
                processed["goat_id"] = None
    
    return processed


@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin():
    """Admin dashboard."""
    from flask_login import current_user
    
    if request.method == "POST":
        action = request.form.get("action")

        match action:
            case "edit":
                table_name = request.form["table_name"]
                return redirect(url_for("admin_table", table_name=table_name))
            case "cancel":
                return redirect(url_for("index"))

    tables = list(crud.get_all_tables().keys())
    
    # Gather stats for dashboard
    stats = {
        "soaps": Soap.query.count(),
        "does": Doe.query.count(),
        "foundation": Foundation.query.count(),
        "images": Image.query.count()
    }
    
    return render_template("admin.html", tables=tables, stats=stats, current_user=current_user)


@app.route("/admin/<table_name>", methods=["GET", "POST"])
@login_required
def admin_table(table_name):
    """Admin table display and management page."""
    if request.method == "POST":
        action = request.form.get("action")

        match action:
            case "add":
                column_data = {}
                image_is_uploaded = False
                image_id = None

                # Handle image upload or selection
                if "image" in request.files:
                    image = request.files["image"]
                    if image and image.filename and allowed_file(image.filename):
                        filename = secure_filename(image.filename)
                        directory = request.form.get("directory", "").strip() if table_name == "images" else ""
                        file_path = os.path.join(app.config["UPLOAD_FOLDER"], directory, filename)

                        if os.path.exists(file_path):
                            flash(f"Error: Image with filename '{filename}' already exists", "error")
                            return redirect(url_for("admin_table", table_name=table_name))

                        if table_name == "images":
                            os.makedirs(os.path.join(app.config["UPLOAD_FOLDER"], directory), exist_ok=True)
                            image.save(file_path)
                            column_data["filename"] = filename
                            column_data["directory"] = directory
                            flash(f"Info: Uploaded '{filename}'", "info")
                            image_is_uploaded = True
                        else:
                            try:
                                crud.add_table_row("images", {"filename": filename, "directory": directory})
                                new_image = crud.search_table_row("images", {"filename": filename})
                                image_id = new_image.get("id") if new_image else None
                                image.save(file_path)
                                flash(f"Info: Uploaded '{filename}'", "info")
                                image_is_uploaded = True
                            except sqlalchemy.exc.IntegrityError:
                                flash(f"Error: Image already exists", "error")
                                return redirect(url_for("admin_table", table_name=table_name))
                    elif table_name == "images":
                        flash(f"Error: Please select a photo to upload", "error")
                        return redirect(url_for("admin_table", table_name=table_name))

                # Handle image selection from library (for non-images tables)
                selected_image_id = request.form.get("image_id")
                if selected_image_id and not image_is_uploaded and table_name != "images":
                    try:
                        image_id = int(selected_image_id)
                        if not Image.query.get(image_id):
                            image_id = None
                    except (ValueError, TypeError):
                        image_id = None

                # Set image_id for tables that need it
                if image_id and table_name != "images":
                    column_data["image_id"] = image_id

                # Process other form fields
                user_fields = get_user_fields_for_table(table_name)
                for field in user_fields:
                    field_name = field["name"]
                    if field_name in request.form and field_name not in ["image", "image_upload"]:
                        value = request.form.get(field_name, "").strip()
                        if field["type"] == "password" and not value:
                            continue
                        if field["type"] == "number" and value:
                            try:
                                column_data[field_name] = float(value)
                            except ValueError:
                                pass
                        else:
                            column_data[field_name] = value

                # Handle special cases for does/foundation (need goat_id)
                if table_name in ["does", "foundation", "adoptions"] and "name" in column_data:
                    goat_name = column_data.pop("name")
                    goat = Goat.query.filter_by(name=goat_name).first()
                    if not goat:
                        goat = Goat(name=goat_name)
                        db.session.add(goat)
                        db.session.commit()
                    column_data["goat_id"] = goat.id

                # Add note for images table
                if table_name == "images" and "note" in request.form:
                    column_data["note"] = request.form.get("note", "").strip()

                # Process column data (handle special conversions)
                column_data = process_column_data(column_data)

                try:
                    crud.add_table_row(table_name, column_data)
                    flash(f"Success: Added to '{table_name}'", "success")
                except Exception as e:
                    if image_is_uploaded and table_name != "images":
                        try:
                            filename = secure_filename(image.filename)
                            directory = request.form.get("directory", "") if table_name == "images" else ""
                            file_path = os.path.join(app.config["UPLOAD_FOLDER"], directory, filename)
                            if os.path.exists(file_path):
                                os.remove(file_path)
                        except:
                            pass
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
                            flash(f"Info: Deleted empty folder '{directory}'", "info")
                        flash(f"Info: Deleted '{filename}'", "info")
                crud.delete_table_row(table_name, row_id)
                flash(f"Success: Deleted from '{table_name}'", "success")

            case "cancel":
                return redirect(url_for("admin"))

    # Pagination support
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)
    
    # Get total count for pagination
    model_class = crud.get_model_class(table_name)
    if model_class:
        total_count = model_class.query.count()
    else:
        table_data = crud.get_table(table_name)
        total_count = len(table_data["table_rows"]) if table_data["table_rows"] else 0
    
    # Get paginated data
    offset = (page - 1) * per_page
    table_rows = crud.get_table_rows(table_name, limit=per_page, offset=offset)
    
    # Build table dict with pagination info
    table = crud.get_all_tables()[table_name]
    table["table_rows"] = table_rows
    table["pagination"] = {
        "page": page,
        "per_page": per_page,
        "total": total_count,
        "pages": (total_count + per_page - 1) // per_page
    }
    
    return render_template("admin_table.html", table_name=table_name, table=table)


@app.route("/api/admin/<table_name>/<int:row_id>", methods=["DELETE"])
@login_required
def api_delete_row(table_name, row_id):
    """API endpoint to delete a row via AJAX."""
    try:
        if table_name == "images":
            image_row = crud.get_table_row(table_name, row_id)
            filename = image_row.get("filename")
            directory = image_row.get("directory", "")
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], directory, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                directory_path = os.path.join(app.config["UPLOAD_FOLDER"], directory)
                if len(os.listdir(directory_path)) == 0:
                    os.rmdir(directory_path)
        crud.delete_table_row(table_name, row_id)
        return jsonify({"success": True, "message": f"Deleted from '{table_name}'"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/admin/<table_name>", methods=["GET"])
@login_required
def api_get_table(table_name):
    """API endpoint to get table data with pagination."""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)
    search = request.args.get("search", "")
    
    # Get total count
    model_class = crud.get_model_class(table_name)
    if model_class:
        total_count = model_class.query.count()
    else:
        table_data = crud.get_table(table_name)
        total_count = len(table_data["table_rows"]) if table_data["table_rows"] else 0
    
    # Get paginated data
    offset = (page - 1) * per_page
    table_rows = crud.get_table_rows(table_name, limit=per_page, offset=offset)
    
    # Get column info
    table = crud.get_all_tables()[table_name]
    
    return jsonify({
        "success": True,
        "data": table_rows,
        "columns": table["table_columns"],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total_count,
            "pages": (total_count + per_page - 1) // per_page
        }
    })


@app.route("/admin/<table_name>/edit/<row_id>", methods=["GET", "POST"])
@login_required
def admin_edit(table_name, row_id):
    """Admin edit page for a specific record."""
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

                # Process form fields
                user_fields = get_user_fields_for_table(table_name)
                for field in user_fields:
                    field_name = field["name"]
                    if field_name in request.form and field_name != "image":
                        value = request.form.get(field_name, "").strip()
                        if field["type"] == "password" and not value:
                            continue
                        if field["type"] == "password":
                            column_data[field_name] = bcrypt.generate_password_hash(value).decode("utf-8")
                        elif field["type"] == "number" and value:
                            try:
                                column_data[field_name] = float(value)
                            except ValueError:
                                pass
                        else:
                            column_data[field_name] = value

                # Handle image upload - always creates new image record (preserves original)
                if "image" in request.files:
                    image = request.files["image"]
                    if image and image.filename and allowed_file(image.filename):
                        existing_image_id = crud.get_table_row_column(table_name, row_id, "image_id")
                        existing_image = Image.query.get(existing_image_id) if existing_image_id else None
                        
                        if table_name == "images":
                            # Editing an image record itself - overwrite the file
                            image_row = crud.get_table_row(table_name, row_id)
                            existing_filename = image_row.get("filename")
                            existing_directory = image_row.get("directory", "")
                            existing_file_path = os.path.join(app.config["UPLOAD_FOLDER"], existing_directory, existing_filename)

                            filename = secure_filename(existing_filename)
                            file_path = os.path.join(app.config["UPLOAD_FOLDER"], existing_directory, filename)
                            os.makedirs(os.path.join(app.config["UPLOAD_FOLDER"], existing_directory), exist_ok=True)

                            if os.path.exists(existing_file_path):
                                os.remove(existing_file_path)

                            image.save(file_path)
                            flash(f"Info: Photo updated", "info")
                        else:
                            # For soaps/does/foundation: always upload as new image (preserve original)
                            directory = request.form.get("image_directory", "").strip()
                            filename = secure_filename(image.filename)
                            
                            # Generate unique filename if needed
                            base_name, ext = os.path.splitext(filename)
                            counter = 1
                            while True:
                                test_path = os.path.join(app.config["UPLOAD_FOLDER"], directory, filename)
                                if not os.path.exists(test_path):
                                    break
                                filename = f"{base_name}_{counter}{ext}"
                                counter += 1
                            
                            file_path = os.path.join(app.config["UPLOAD_FOLDER"], directory, filename)
                            os.makedirs(os.path.dirname(file_path), exist_ok=True)
                            image.save(file_path)
                            
                            # Create new image record
                            new_image = Image(filename=filename, directory=directory)
                            db.session.add(new_image)
                            db.session.commit()
                            
                            # Update the record to point to new image
                            column_data["image_id"] = new_image.id
                            flash(f"Info: New photo uploaded and linked", "info")

                # Handle image selection from library (only if no new image uploaded)
                selected_image_id = request.form.get("image_id")
                if selected_image_id and not ("image" in request.files and request.files["image"].filename):
                    try:
                        new_image_id = int(selected_image_id)
                        # Only update if it's different from current
                        current_image_id = crud.get_table_row_column(table_name, row_id, "image_id")
                        if Image.query.get(new_image_id) and new_image_id != current_image_id:
                            column_data["image_id"] = new_image_id
                            flash(f"Info: Photo changed", "info")
                    except (ValueError, TypeError):
                        pass

                # Handle name change for goat-related tables
                if table_name in ["does", "foundation", "adoptions"] and "name" in column_data:
                    new_name = column_data.pop("name")
                    goat_id = crud.get_table_row_column(table_name, row_id, "goat_id")
                    if goat_id and new_name:
                        goat = Goat.query.get(int(goat_id))
                        if goat:
                            goat.name = new_name
                            db.session.commit()
                            flash(f"Info: Goat name updated to '{new_name}'", "info")

                # Process column data (handle special conversions)
                column_data = process_column_data(column_data)

                try:
                    crud.edit_table_row(table_name, row_id, column_data)
                    flash(f"Success: Changes saved", "success")
                except Exception as e:
                    flash(f"Error: {e}", "error")
                    return redirect(url_for("admin_table", table_name=table_name))
                return redirect(url_for("admin_table", table_name=table_name))

            case "cancel":
                return redirect(url_for("admin_table", table_name=table_name))

    table = crud.get_all_tables()[table_name]
    return render_template("admin_edit.html", table_name=table_name, table=table, row_id=row_id)


@app.route("/admin/export", methods=["GET", "POST"])
@login_required
def admin_export():
    """Export database to JSON file for download."""
    if request.method == "POST":
        export_data = export_database()
        
        temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8")
        json.dump(export_data, temp_file, indent=2, default=str)
        temp_file.close()
        
        filename = f"goatmountainview_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"
        
        try:
            return send_file(
                temp_file.name,
                as_attachment=True,
                download_name=filename,
                mimetype="application/json"
            )
        finally:
            import time
            time.sleep(0.1)
            try:
                os.unlink(temp_file.name)
            except Exception:
                pass
    
    return render_template("admin_export.html")


@app.route("/admin/import", methods=["GET", "POST"])
@login_required
def admin_import():
    """Import database from JSON file."""
    if request.method == "POST":
        if "file" not in request.files:
            flash("Error: No file uploaded", "error")
            return redirect(url_for("admin_import"))
        
        file = request.files["file"]
        
        if file.filename == "":
            flash("Error: No file selected", "error")
            return redirect(url_for("admin_import"))
        
        if not file.filename.endswith(".json"):
            flash("Error: Please upload a JSON file", "error")
            return redirect(url_for("admin_import"))
        
        try:
            export_data = json.load(file)
            stats = import_database(export_data)
            
            if stats["errors"]:
                for error in stats["errors"]:
                    flash(f"Error: {error}", "error")
            
            flash(f"Success: Imported {stats["tables_imported"]} tables with {stats["rows_imported"]} rows", "success")
            
            if stats.get("notes"):
                for note in stats["notes"]:
                    flash(f"Note: {note}", "info")
            
        except Exception as e:
            flash(f"Error: Import failed - {str(e)}", "error")
        
        return redirect(url_for("admin"))
    
    return render_template("admin_import.html")
