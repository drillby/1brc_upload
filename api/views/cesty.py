import os
from concurrent.futures import ThreadPoolExecutor
from functools import partial

from flask import flash, redirect, render_template, request, url_for

from api import app
from api.helper import SMTPHandler, allowed_file, run_script

from ..messages import EmailMessages, FileUploadMessages


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

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
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

    executor = ThreadPoolExecutor(thread_name_prefix="flask-script-executor")
    executor.submit(
        run_script,
        file_path=file_path,
        action=action,
        timeout=app.config["TIMEOUT"],
    )
    # TODO: přesunout do tempdir i measurements.txt a zkusit spustit

    """# create temp dir
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
    shutil.rmtree(temp_dir)"""

    return redirect(url_for("index"))
