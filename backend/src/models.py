import os
from datetime import datetime
import json
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, DATETIME, Enum, Float
from sqlalchemy.orm import relationship, backref
from flask_login import UserMixin
from enum import Enum as RoleEnum

from backend.src import db, app


class UserEnum(RoleEnum):
    USER = 1
    ADMIN = 2
    TEACHER = 3

class Base(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    active = Column(Boolean, default=True)
    created_date = Column(DateTime, default=datetime.now())
    def __str__(self):
        return self.name

class User(Base, UserMixin):
    username = Column(String(150), nullable=False, unique=True)
    password = Column(String(150), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    avatar = Column(String(300), default="https://res.cloudinary.com/deeqcwnpm/image/upload/v1764919829/cld-sample.jpg")
    role = Column(Enum(UserEnum), nullable=False, default=UserEnum.USER)



class Capdo(Base):
    khoahocs = relationship('Khoahoc', backref="Capdo", lazy=True)



class Khoahoc(Base):
    capDo_id = Column(Integer, ForeignKey(Capdo.id), nullable=False)
    hocPhi = Column(Integer, nullable=False)
    image = Column(String(300), default='https://res.cloudinary.com/deeqcwnpm/image/upload/v1765041156/daily_conversational_english_p81vyi.png')
    description = Column(String(300))



if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        c1 = Capdo(name="Beginner")
        c2 = Capdo(name="Intermediate")
        c3 = Capdo(name="Advanced")
        db.session.add_all([c1, c2, c3])

        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        json_path = os.path.join(BASE_DIR, 'database', 'khoahoc.json')

        with open(json_path, encoding="utf-8") as f:
            khoahoc = json.load(f)

            for k in khoahoc:
                db.session.add(Khoahoc(**k))

            db.session.commit()


        import hashlib

        # Tạo user mẫu
        u1 = User(name="Admin", username="admin",
          password=str(hashlib.md5("123".encode("utf-8")).hexdigest()), email ="admin@gmail.com", role=UserEnum.ADMIN)
        u2 = User(name="User", username="user",
          password=str(hashlib.md5("123".encode("utf-8")).hexdigest()), email ="user@gmail.com", role=UserEnum.USER)
        u3 = User(name="TEACHER", username="teacher",
          password=str(hashlib.md5("123".encode("utf-8")).hexdigest()), email ="teacher@gmail.com", role=UserEnum.TEACHER)

        db.session.add_all([u1,u2,u3])
        db.session.commit()