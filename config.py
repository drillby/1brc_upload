import hashlib
import os
import random
import string


class Config:
    SECRET_KEY = os.getenv(
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
    MAX_CONTENT_LENGTH = eval(os.getenv("MAX_CONTENT_LENGTH", str(1)) + "* 1024 * 1024")
    ALLOWED_EXTENSIONS = set(os.getenv("ALLOWED_EXTENSIONS", "py").split(","))
    TIMEOUT = eval(os.getenv("TIMEOUT", str(0.5) + " * 60"))
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")


class ProductionConfig(Config):
    DEBUG = False
    EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    SMTP_SERVER = os.getenv("SMTP_SERVER")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    ALLOWED_DOMAINS = set(os.getenv("ALLOWED_DOMAINS", "spskladno.cz").split(","))
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
