from app import app


def allowed_file(filename) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]


def table_to_model(table_name) -> str:
    model_name = table_name
    if model_name.endswith("s"):
        model_name = model_name[:-1]
    return model_name.capitalize()
