from typing import List
from PIL import Image
from app import app


def allowed_file(filename) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]


def total_images_width(filenames: List[str]) -> int:
    total_width = 0
    for filename in filenames:
        with Image.open(filename) as img:
            total_width += img.width
    return total_width


def split_file_path(file_path: str) -> tuple:
    split_path = file_path.rsplit("/", 1)
    if len(split_path) > 1:
        directory = split_path[0]
        filename = split_path[1]
    else:
        directory = ""
        filename = file_path
    return directory, filename
