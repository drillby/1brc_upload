import hashlib
import os
import random
import string
import tempfile
from concurrent.futures import ThreadPoolExecutor
from functools import partial

from flask import Flask, flash, redirect, render_template, request, url_for

from api.models.user import db

from .helper import SMTPHandler, run_script
from .messages import EmailMessages, FileUploadMessages

app = Flask(__name__)


try:
    app.config.from_object("config.Config")
except Exception as e:
    # load config from os.getenv if config.py is not found
    app.config["SECRET_KEY"] = os.getenv(
        "SECRET_KEY",
        hashlib.sha256(
            bytes(
                "{}".format(
                    "".join(
                        random.choices(string.ascii_uppercase + string.digits, k=16)
                    )
                ),
                encoding="utf-8",
            )
        ).hexdigest(),
    )
    app.config["UPLOAD_FOLDER"] = os.getenv("UPLOAD_FOLDER", "uploads")
    app.config["MAX_CONTENT_LENGTH"] = eval(
        os.getenv("MAX_CONTENT_LENGTH", str(1 * 1024 * 1024))
    )
    app.config["ALLOWED_EXTENSIONS"] = set(os.getenv("ALLOWED_EXTENSIONS", {"py"}))
    app.config["TIMEOUT"] = eval(os.getenv("TIMEOUT", str(15 * 60)))

    app.config["EMAIL_ADDRESS"] = os.getenv("EMAIL_ADDRESS")
    app.config["EMAIL_PASSWORD"] = os.getenv("EMAIL_PASSWORD")
    app.config["SMTP_SERVER"] = os.getenv("SMTP_SERVER")
    app.config["SMTP_PORT"] = int(os.getenv("SMTP_PORT", 587))
    app.config["ALLOWED_DOMAINS"] = os.getenv("ALLOWED_DOMAINS", {"spskladno.cz"})
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")

db.init_app(app)
with app.app_context():
    db.create_all()


executor = ThreadPoolExecutor()


if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])


def allowed_file(filename: str):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
    )


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

    if not (file and allowed_file(file.filename)):
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

    with tempfile.NamedTemporaryFile() as temp:
        temp.write(file.read())
        temp.flush()
        temp.seek(0)

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
            file_path=temp.name,
            action=action,
            timeout=app.config["TIMEOUT"],
        )

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
