import uuid

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "1brc"
    id = db.Column(
        db.String(len(str(uuid.uuid1()))),
        primary_key=True,
        default=uuid.uuid1,
    )
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), unique=False, nullable=False)
    file_name = db.Column(db.String(120), unique=False, nullable=False)
    time = db.Column(db.Integer, unique=False, default=0, nullable=False)

    def __repr__(self):
        return f"<User {self.email}>"

    def __init__(self, email, password, file_name) -> None:
        self.email = email
        self.password = password
        self.file_name = file_name
