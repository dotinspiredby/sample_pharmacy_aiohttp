from dataclasses import dataclass
from hashlib import sha256
from typing import Optional

from app.store.database.gino_ import db


@dataclass
class Admin:
    id: int
    login: str
    password: Optional[str] = None

    def is_password_valid(self, password: str):
        return self.password == sha256(password.encode()).hexdigest()

    @classmethod
    def from_session(cls, session: Optional[dict]):
        return cls(id=session["admin"]["id"],
                   login=session["admin"]["login"])


class AdminModel(db.Model):
    __tablename__ = "admins"

    id = db.Column(db.Integer(), primary_key=True)
    login = db.Column(db.Unicode(), nullable=False)
    password = db.Column(db.String(), nullable=False)
