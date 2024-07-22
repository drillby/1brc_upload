import os
from concurrent.futures import ThreadPoolExecutor
from functools import partial

from flask import flash, redirect, render_template, request, send_file, url_for

from api import app
from api.helper import SMTPHandler, allowed_email_domain, allowed_file, run_script

from ..messages import EmailMessages, FileUploadMessages, MessageType, UserMessages
from ..models.user import User, db


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/", methods=["POST"])
def upload_file():
    # get email and password from form
    email = request.form.get("email")
    password = request.form.get("password")

    # get file from form
    file = request.files.get("file")
    filename = file.filename

    # check if email and password are not empty
    if not email or not password:
        flash(UserMessages.MISSING_CREDENTIALS.value, MessageType.ERROR.value)
        return redirect(request.url)

    if not allowed_email_domain(email, app.config["ALLOWED_DOMAINS"]):
        flash(
            UserMessages.WRONG_EMAIL_DOMAIN.value.format(
                domains=", ".join(app.config["ALLOWED_DOMAINS"])
            ),
            MessageType.ERROR.value,
        )
        return redirect(request.url)

    # check if user exists
    user = User.query.filter_by(email=email).first()
    is_new_user = False

    # if user does not exist, create new user
    if not user:
        user = User(
            email=email,
            password=password,
        )
        db.session.add(user)
        db.session.commit()
        is_new_user = True
        flash(UserMessages.USER_CREATED.value, MessageType.INFORMATION.value)

    # if user exists, check password
    if not is_new_user and not user.check_password(password):
        flash(UserMessages.WRONG_PASSWORD.value, MessageType.ERROR.value)
        return redirect(request.url)

    # check if file was uploaded
    if "file" not in request.files:
        flash(FileUploadMessages.NO_FILE_SELECTED.value, MessageType.ERROR.value)
        return redirect(request.url)

    # check if file is empty
    if file.filename == "":
        flash(FileUploadMessages.NO_FILE_SELECTED.value, MessageType.ERROR.value)
        return redirect(request.url)

    # check if file is allowed
    if not (file and allowed_file(file.filename, app.config["ALLOWED_EXTENSIONS"])):
        flash(
            FileUploadMessages.WRONG_FILE_FORMAT.value.format(
                formats=", ".join(app.config["ALLOWED_DOMAINS"])
            ),
            MessageType.ERROR.value,
        )
        return redirect(request.url)

    # check if file is not too big
    if file.content_length > app.config["MAX_CONTENT_LENGTH"]:
        flash(
            FileUploadMessages.SIZE_LIMIT_EXCEEDED.value.format(
                size=int(app.config["MAX_CONTENT_LENGTH"] / 1024 / 1024)
            ),
            MessageType.ERROR.value,
        )
        return redirect(request.url)

    # check if file is close to limit size (80%)
    if file.content_length > app.config["MAX_CONTENT_LENGTH"] * 0.8:
        flash(
            FileUploadMessages.SIZE_LIMIT_WARNING.value.format(
                size=int(app.config["MAX_CONTENT_LENGTH"] / 1024 / 1024)
            ),
            MessageType.WARNING.value,
        )

    # save file
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], email.split("@")[0] + ".py")

    file.save(file_path)

    flash(FileUploadMessages.FILE_UPLOADED.value, MessageType.SUCCESS.value)

    # prepare email
    smtp = SMTPHandler(
        app.config["EMAIL_ADDRESS"],
        app.config["EMAIL_PASSWORD"],
        app.config["SMTP_SERVER"],
        app.config["SMTP_PORT"],
    )

    # prepare action
    action = partial(
        smtp.send_email,
        email_address=email,
        subject=EmailMessages.HEADER.value,
    )

    # run script in separate thread
    executor = ThreadPoolExecutor(thread_name_prefix="flask-script-executor")
    executor.submit(
        run_script,
        file_path=file_path,
        action=action,
        timeout=app.config["TIMEOUT"],
    )

    return redirect(url_for("index"))


@app.route("/leaderboard")
def leaderboard():
    users = User.query.filter(User.best_time != 0).order_by(User.best_time).all()
    return render_template("leaderboard.html", users=users)
