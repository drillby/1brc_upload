import os
import shutil
import tempfile
from concurrent.futures import ThreadPoolExecutor
from functools import partial

from flask import Flask, flash, redirect, render_template, request, url_for

from api.models.user import db

from .helper import SMTPHandler, run_script
from .messages import EmailMessages, FileUploadMessages

app = Flask(__name__)

deploy = os.getenv("FLASK_ENV", "development")

app.config.from_object("config.Config")
if deploy == "development":
    app.config.from_object("devconf.DevelopmentConfig")
else:
    app.config.from_object("config.ProductionConfig")

db.init_app(app)
with app.app_context():
    db.create_all()


def allowed_file(filename: str, allwed_extensions: set):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allwed_extensions


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        flash(FileUploadMessages.NO_FILE_SELECTED.value, "error")
        return redirect(request.url)

    file = request.files.get("file")

    if file.filename == "":
        flash(FileUploadMessages.NO_FILE_SELECTED.value, "error")
        return redirect(request.url)

    if not (file and allowed_file(file.filename, app.config["ALLOWED_EXTENSIONS"])):
        flash(FileUploadMessages.WRONG_FILE_FORMAT.value, "error")
        return redirect(request.url)

    if file.content_length > app.config["MAX_CONTENT_LENGTH"]:
        flash(FileUploadMessages.SIZE_LIMIT_EXCEEDED.value, "error")
        return redirect(request.url)

    filename = file.filename

    """file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(file_path)

    flash(FileUploadMessages.FILE_UPLOADED.value, "success")

    smtp = SMTPHandler(
        app.config["EMAIL_ADDRESS"],
        app.config["EMAIL_PASSWORD"],
        app.config["SMTP_SERVER"],
        app.config["SMTP_PORT"],
    )

    action = partial(
        smtp.send_email,
        email_address=request.form.get("email"),
        subject=EmailMessages.HEADER.value,
    )

    executor.submit(
        run_script,
        file_path=file_path,
        action=action,
        timeout=app.config["TIMEOUT"],
    )"""
    # TODO: přesunout do tempdir i measurements.txt a zkusit spustit

    # create temp dir
    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, filename)
    file.save(file_path)

    current_dir = os.getcwd()
    measurements_path = os.path.join(current_dir, "api", "static", "measurements.txt")

    data_dir = os.path.join(temp_dir, "data")
    os.makedirs(data_dir)

    shutil.copy(measurements_path, data_dir)

    flash(FileUploadMessages.FILE_UPLOADED.value, "success")

    smtp = SMTPHandler(
        app.config["EMAIL_ADDRESS"],
        app.config["EMAIL_PASSWORD"],
        app.config["SMTP_SERVER"],
        app.config["SMTP_PORT"],
    )

    action = partial(
        smtp.send_email,
        email_address=request.form.get("email"),
        subject=EmailMessages.HEADER.value,
    )

    executor = ThreadPoolExecutor(thread_name_prefix="flask-script-executor")

    executor.submit(
        run_script,
        file_path=file_path,
        action=action,
        timeout=app.config["TIMEOUT"],
    )

    # remove temp dir and all its content
    shutil.rmtree(temp_dir)

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run()
