import json
import os
from datetime import datetime
from enum import Enum as RoleEnum
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, Enum, Float
from sqlalchemy.orm import relationship
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
    password = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    avatar = Column(String(300), default="https://res.cloudinary.com/deeqcwnpm/image/upload/v1764919829/cld-sample.jpg")
    role = Column(Enum(UserEnum), nullable=False, default=UserEnum.USER)
    enrollments = relationship('Enrollment', backref='user', lazy=True)


class Capdo(Base):
    khoahocs = relationship('Khoahoc', backref="Capdo", lazy=True)

class Khoahoc(Base):
    capDo_id = Column(Integer, ForeignKey(Capdo.id), nullable=False)
    hocPhi = Column(Integer, nullable=False)
    image = Column(String(300),
                   default='https://res.cloudinary.com/deeqcwnpm/image/upload/v1765041156/daily_conversational_english_p81vyi.png')
    description = Column(String(300))
    questions = relationship('Question', backref="khoahoc", lazy=True, cascade='all, delete-orphan')
    lessons = relationship('Lesson', backref='khoahoc', cascade='all, delete-orphan')
    enrollments = relationship('Enrollment', backref='khoahoc_enroll', lazy=True, cascade="all, delete-orphan")
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    user = relationship('User', backref='khoahoc_user', lazy=True)

class Lesson(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    content = Column(Text)
    video_url = Column(String(300))
    khoahoc_id = Column(Integer, ForeignKey(Khoahoc.id), nullable=False)
    questions = db.relationship('Question',backref='lesson',cascade='all, delete-orphan')


class Question(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(String(500), nullable=False)
    khoahoc_id = Column(Integer, ForeignKey(Khoahoc.id), nullable=False)
    lesson_id = Column(Integer, ForeignKey(Lesson.id), nullable=False)
    answers = relationship('Answer', backref="question", lazy=True, cascade="all, delete-orphan")

class Answer(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    answer = Column(String(500), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    question_id = Column(Integer, ForeignKey(Question.id), nullable=False)


class Progress(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    khoahoc_id = Column(Integer, ForeignKey(Khoahoc.id), nullable=False)

    lesson_id = Column(Integer, ForeignKey(Lesson.id), nullable=True)

    is_completed = Column(Boolean, default=False)
    score = Column(Float, nullable=True)
    date = Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())



class Enrollment(db.Model):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    khoahoc_id = Column(Integer, ForeignKey(Khoahoc.id), nullable=False)
    created_date = Column(DateTime, default=datetime.now())


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        # Tạo cấp độ
        c1 = Capdo(name="Beginner")
        c2 = Capdo(name="Intermediate")
        c3 = Capdo(name="Advanced")
        db.session.add_all([c1, c2, c3])
        db.session.commit()

        # Tạo User
        import hashlib

        u1 = User(name="Admin", username="admin", password=str(hashlib.md5("123".encode("utf-8")).hexdigest()),
                  email="admin@gmail.com", role=UserEnum.ADMIN)
        u2 = User(name="Hoa", username="sv1", password=str(hashlib.md5("123".encode("utf-8")).hexdigest()),
                  email="sv1@gmail.com", role=UserEnum.USER)
        u3 = User(name="Huy", username="gv1", password=str(hashlib.md5("123".encode("utf-8")).hexdigest()),
                  email="gv1@gmail.com", role=UserEnum.TEACHER)
        u4 = User(name="Hạnh", username="gv2", password=str(hashlib.md5("123".encode("utf-8")).hexdigest()),
                  email="gv2@gmail.com", role=UserEnum.TEACHER)
        db.session.add_all([u1, u2, u3, u4])
        db.session.commit()

        # Insert bảng ...

        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        json_path = os.path.join(BASE_DIR, 'database')

        with open(os.path.join(json_path, 'khoahoc.json'), encoding="utf-8") as f:
            khoahoc = json.load(f)
            for k in khoahoc:
                db.session.add(Khoahoc(**k))
            db.session.commit()

        with open(os.path.join(json_path, 'lesson.json'), encoding="utf-8") as f:
            lesson = json.load(f)
            for l in lesson:
                db.session.add(Lesson(**l))
            db.session.commit()

        with open(os.path.join(json_path, 'question.json'), encoding="utf-8") as f:
            question = json.load(f)
            for q in question:
                db.session.add(Question(**q))
            db.session.commit()

        with open(os.path.join(json_path, 'answer.json'), encoding="utf-8") as f:
            answer = json.load(f)
            for a in answer:
                db.session.add(Answer(**a))
            db.session.commit()




