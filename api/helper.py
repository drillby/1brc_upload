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
from typing import Optional, Union

from api.main import db

from .messages import EmailMessages
from .models.user import User


def run_script(file_path, timeout, action):
    try:
        start = time.time()
        subprocess.run(
            ["python", file_path],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        end = time.time()
        runtime = end - start

        action(
            body=EmailMessages.SUCCESS.value.format(runtime=runtime)
            + "\n"
            + EmailMessages.FOOTER.value
        )
    except Exception as e:
        if isinstance(e, subprocess.TimeoutExpired):
            action(
                body=EmailMessages.TIMEOUT.value.format(timeout=timeout)
                + "\n"
                + EmailMessages.FOOTER.value
            )
        else:
            action(body=EmailMessages.RUNTIME_ERROR.value.format(error=e))


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


def hash_password(password: str) -> str:
    return hashlib.sha512(password.encode()).hexdigest()


if __name__ == "__main__":
    print(len(hash_password("password")))
