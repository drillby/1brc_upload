import uuid

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "1brc"
    id = db.Column(
        db.String(len(str(uuid.uuid1()))),
        primary_key=True,
        default=uuid.uuid1,
    )
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(162), unique=False, nullable=False)
    file_name = db.Column(db.String(120), unique=False, nullable=True)
    best_time = db.Column(db.Float, unique=False, default=0, nullable=False)

    def __init__(self, email, password, file_name=None) -> None:
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.file_name = file_name

    def __repr__(self):
        return f"<User {self.email}>"

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)
