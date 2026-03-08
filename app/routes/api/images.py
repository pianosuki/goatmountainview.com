"""
API Routes

JSON API endpoints for AJAX requests.
"""

from flask import jsonify, request
from flask_login import login_required
from app import app, db
from app.models import Image


@app.route("/api/images", methods=["GET"])
@login_required
def api_get_images():
    """API endpoint to get images by folder (lazy loading)."""
    import os
    
    folder = request.args.get("folder", "")
    upload_folder = app.config["UPLOAD_FOLDER"]
    
    # Get all actual folders from filesystem
    all_folders = []
    if os.path.exists(upload_folder):
        for item in os.listdir(upload_folder):
            item_path = os.path.join(upload_folder, item)
            if os.path.isdir(item_path):
                all_folders.append(item)
    
    # Also get folders from database
    db_folders = db.session.query(Image.directory).distinct().all()
    db_folder_list = [f[0] for f in db_folders if f[0] and f[0] not in all_folders]
    all_folders.extend(db_folder_list)
    
    # Get images from database
    if folder:
        db_images = Image.query.filter_by(directory=folder).all()
    else:
        db_images = Image.query.filter_by(directory="").all()
    
    # Also scan filesystem for images in this folder
    fs_images = []
    if folder:
        folder_path = os.path.join(upload_folder, folder)
    else:
        folder_path = upload_folder
    
    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            if filename.lower().endswith((".jpg", ".jpeg", ".png")):
                existing = next((img for img in db_images if img.filename == filename), None)
                if not existing:
                    fs_images.append({
                        "id": f"fs_{filename}",
                        "filename": filename,
                        "directory": folder,
                        "url": f"/static/images/uploads/{folder}/{filename}" if folder else f"/static/images/uploads/{filename}",
                        "note": "Upload to add to library",
                        "is_filesystem": True
                    })
    
    result = {
        "folders": sorted(all_folders),
        "current_folder": folder,
        "images": [
            {
                "id": img.id,
                "filename": img.filename,
                "directory": img.directory,
                "url": f"/static/images/uploads/{img.directory}/{img.filename}" if img.directory else f"/static/images/uploads/{img.filename}",
                "note": img.note or ""
            }
            for img in db_images
        ] + fs_images
    }
    
    return jsonify(result)
