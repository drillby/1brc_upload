import uuid
from datetime import datetime

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
    fk_class = db.Column(
        db.Integer,
        db.ForeignKey("1brc_class.id"),
        nullable=False,
    )

    def __init__(self, email, password, fk_class, file_name=None) -> None:
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.file_name = file_name
        self.fk_class = fk_class

    def __repr__(self):
        return f"<User {self.email}>"

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Class(db.Model):
    __tablename__ = "1brc_class"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    field_of_study = db.Column(db.String(3), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    __table_args__ = (db.UniqueConstraint("field_of_study", "year"),)

    def __init__(self, field_of_study, year) -> None:
        self.field_of_study = field_of_study
        self.year = year

    def __repr__(self):
        return f"<Class {self.field_of_study} {self.year}>"

    def __str__(self):
        return f"{self.field_of_study}{self.grade}"

    @property
    def grade(self) -> int:
        start_year = self.year
        current_year = datetime.now().year
        shift = 0 if datetime.now().month < 9 else 1
        return current_year - start_year + shift


if __name__ == "__main__":
    class_ = Class("EP", 2020)
    print(class_.grade)
