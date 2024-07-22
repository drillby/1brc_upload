import hashlib
import smtplib
import ssl
import subprocess
import time
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os import PathLike
from pathlib import Path
from typing import Callable, Iterable, Optional, Union

from api import app

from .messages import EmailMessages
from .models.user import User, db


def allowed_file(filename: str, allwed_extensions: Iterable[str]) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allwed_extensions


def allowed_email_domain(email: str, allowed_domains: Iterable[str]) -> bool:
    return email.rsplit("@", 1)[1].lower() in allowed_domains


def run_script(file_path: PathLike, timeout: int, action: Callable) -> None:
    try:
        # run script
        start = time.time()
        res = subprocess.run(
            ["python", file_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=True,
        )

        end = time.time()
        runtime = end - start
        if res.returncode != 0:
            raise Exception(res.stderr)
        with open("uploads/data/correct_output.txt", "r") as f:
            correct_output = f.read().strip()
        output = res.stdout.strip()

        is_same = compare_strings(correct_output, output)

        base_message = (
            EmailMessages.SUCCESS.value.format(runtime=runtime)
            if is_same
            else EmailMessages.DIFFERENT_RESULTS.value
        )
        email_body = f"{base_message}{EmailMessages.NEW_LINE.value}{EmailMessages.MATCHING_RESULTS.value if is_same else EmailMessages.DIFFERENT_RESULTS.value}{EmailMessages.NEW_LINE.value}{EmailMessages.NEW_LINE.value}{EmailMessages.FOOTER.value}"

        # send email with results
        action(body=email_body)

        # update best time if needed
        with app.app_context():
            user_to_update: User = User.query.filter_by(
                email=action.keywords["email_address"]
            ).first()

            if (
                user_to_update
                and is_same
                and (
                    user_to_update.best_time == 0 or runtime < user_to_update.best_time
                )
            ):
                user_to_update.best_time = runtime
                user_to_update.file_name = Path(file_path).name
                db.session.commit()

    except Exception as e:
        if isinstance(e, subprocess.TimeoutExpired):
            # send email with timeout message
            action(
                body=EmailMessages.TIMEOUT.value.format(timeout=timeout)
                + EmailMessages.NEW_LINE.value
                + EmailMessages.NEW_LINE.value
                + EmailMessages.FOOTER.value
            )
        else:
            # send email with runtime error message
            action(
                body=EmailMessages.RUNTIME_ERROR.value.format(error=e)
                + EmailMessages.NEW_LINE.value
                + EmailMessages.NEW_LINE.value
                + EmailMessages.FOOTER.value
            )
    finally:
        # delete files that are not in db
        with app.app_context():
            all_files = set(
                [user.file_name for user in User.query.filter(User.file_name != None)]
            )

        all_files_in_uploads = set(
            [
                file.name
                for file in Path(app.config["UPLOAD_FOLDER"]).rglob("*")
                if file.is_file()
            ]
        )

        files_to_delete = all_files_in_uploads - all_files
        for file in files_to_delete:
            if file in ("correct_output.txt", "measurements.txt"):
                continue
            Path(f"{app.config['UPLOAD_FOLDER']}/{file}").unlink()


class SMTPHandler:
    def __init__(
        self, email_address: str, email_password: str, smtp_server: str, smtp_port: int
    ) -> None:
        """SMTPHandler class that takes care of sending mails to clients

        Args:
            email_address (str): sending email address
            email_password (str): sending email pw
            smtp_server (str): smtp server
            smtp_port (str): smtp port
        """
        self.email_address = email_address
        self.email_password = email_password
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port

    @property
    def ssl_context(self) -> ssl.SSLContext:
        return ssl.create_default_context()

    def __create_mail(
        self,
        email_address: str,
        subject: str,
        body: str,
        filename: Optional[str],
        attachment_path: Union[str, PathLike[str]],
    ) -> MIMEMultipart:
        """Helper function responsible for generating mail

        Args:
            email_address (str): reciever mail address
            subject (str): mail subject
            body (str): mail body
            attachment_path (Optional[PathLike]): attachment path, MUST BE ROOT PATH
            filename (Optional[str]): attachment file name

        Returns:
            MIMEMultipart: mail to send
        """
        message = MIMEMultipart()
        message["From"] = Header(self.email_address)
        message["To"] = Header(email_address)
        message["Subject"] = Header(subject)

        message.attach(MIMEText(body, "plain", "utf-8"))

        try:
            with open(Path(attachment_path), "rb") as f:
                att = MIMEApplication(f.read(), str(attachment_path).split(".")[-1])
            att.add_header("Content-Disposition", "attachment", filename=filename)
            message.attach(att)
        finally:
            return message

    def send_email(
        self,
        email_address: str,
        subject: str,
        body: str,
        att_path: Union[str, PathLike[str]] = "",
        file_name: str = "",
    ) -> None:
        """Function responsible for sending mail

        Args:
            email_address (str): reciever mail address
            subject (str): mail subject
            body (str): mail body
            att_path (Optional[PathLike]): attachment path, MUST BE ROOT PATH
            file_name (Optional[str]): attachment name
        """
        message = self.__create_mail(email_address, subject, body, file_name, att_path)
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls(context=self.ssl_context)
            server.login(self.email_address, self.email_password)
            server.sendmail(self.email_address, email_address, message.as_string())


def compare_strings(s1: str, s2: str) -> bool:
    if len(s1) != len(s2):
        return False

    return hashlib.md5(s1.encode()).hexdigest() == hashlib.md5(s2.encode()).hexdigest()
