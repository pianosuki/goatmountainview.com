"""
Public Routes

Routes for the public-facing website (non-admin).
"""

from flask import render_template
from app import app
from app import crud
from app.utils import total_images_width
import os


@app.route("/")
def index():
    """Homepage."""
    return render_template("index.html")


@app.route("/portfolio")
def portfolio():
    """Portfolio page showing work history."""
    books_hs_table = crud.get_table("books_hs")
    books_st_table = crud.get_table("books_st")
    image_folder = app.config["STATIC_FOLDER"] + "/images/books/"
    image_filenames = [filename for filename in os.listdir(image_folder) if os.path.isfile(os.path.join(image_folder, filename))]
    images_width = total_images_width([image_folder + image for image in image_filenames], 200)
    return render_template("portfolio.html", books_hs=books_hs_table, books_st=books_st_table, slideshow_images=image_filenames, slideshow_width=images_width)


@app.route("/goats")
def goats():
    """Goats overview page."""
    return render_template("goats.html")


@app.route("/goats/does")
def does():
    """Does page showing all female goats."""
    from app.models import Doe
    does_list = Doe.query.all()
    image_folder = app.config["UPLOAD_FOLDER"] + "/does"
    image_paths = [f"/uploads/does/{filename}" for filename in os.listdir(image_folder) if os.path.isfile(os.path.join(image_folder, filename))]
    image_filenames = [filename for filename in os.listdir(image_folder) if os.path.isfile(os.path.join(image_folder, filename))]
    images_width = total_images_width([os.path.join(image_folder, image) for image in image_filenames], 200)
    return render_template("does.html", does=does_list, slideshow_images=image_paths, slideshow_width=images_width)


@app.route("/goats/adoptions")
def adoptions():
    """Adoptions page showing goats available for adoption."""
    image_folder = app.config["UPLOAD_FOLDER"] + "/adoptions"
    image_paths = [f"/uploads/adoptions/{filename}" for filename in os.listdir(image_folder) if os.path.isfile(os.path.join(image_folder, filename))]
    image_filenames = [filename for filename in os.listdir(image_folder) if os.path.isfile(os.path.join(image_folder, filename))]
    images_width = total_images_width([os.path.join(image_folder, image) for image in image_filenames], 200)
    return render_template("adoptions.html", slideshow_images=image_paths, slideshow_width=images_width)


@app.route("/goats/foundation")
def foundation():
    """Foundation goats page."""
    from app.models import Foundation
    foundation_list = Foundation.query.all()
    image_folder = app.config["UPLOAD_FOLDER"] + "/foundation"
    image_paths = [f"/uploads/foundation/{filename}" for filename in os.listdir(image_folder) if os.path.isfile(os.path.join(image_folder, filename))]
    image_filenames = [filename for filename in os.listdir(image_folder) if os.path.isfile(os.path.join(image_folder, filename))]
    images_width = total_images_width([os.path.join(image_folder, image) for image in image_filenames], 200)
    return render_template("foundation.html", foundation=foundation_list, slideshow_images=image_paths, slideshow_width=images_width)


@app.route("/soap")
def soap():
    """Soap products page."""
    from app.models import Soap
    soaps_table = Soap.query.all()
    return render_template("soap.html", soaps=soaps_table)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    """Contact form page."""
    from flask import redirect, url_for, flash, request
    
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
