import hashlib

from backend.src.models import User, Khoahoc, Lesson, Progress, Capdo, UserEnum
from backend.src import db
from backend.src.dao import auth_user, update_user_progress


def test_update_lesson_progress_success(app):
    with app.app_context():

        capdo = Capdo(name="Test Level")
        db.session.add(capdo)
        db.session.commit()

        user = User(name="Sinh Vien Test", username="sv_test", password="123", email="sv@test.com", role=UserEnum.USER)
        db.session.add(user)
        db.session.commit()


        khoahoc = Khoahoc(
            name="Khoa hoc Unit Test",
            capDo_id=capdo.id,
            hocPhi=100000,
            description="Khoa hoc Test",
            user_id=user.id
        )
        db.session.add(khoahoc)
        db.session.commit()


        lesson = Lesson(
            title="Bài 1 Test",
            khoahoc_id=khoahoc.id
        )
        db.session.add(lesson)
        db.session.commit()

        initial_progress = Progress(
            user_id=user.id,
            khoahoc_id=khoahoc.id,
            lesson_id=lesson.id,
            is_completed=False,
            score=0
        )
        db.session.add(initial_progress)
        db.session.commit()



        progress_to_update = Progress.query.filter_by(user_id=user.id, lesson_id=1).first()
        progress_to_update.is_completed = True
        progress_to_update.score = 8.5
        db.session.commit()


        updated_progress = Progress.query.filter_by(user_id=user.id, lesson_id=1).first()

        assert updated_progress is not None
        assert updated_progress.is_completed is True
        assert updated_progress.score == 8.5


def test_auth_user_returns_user_with_valid_credentials(app):
    with app.app_context():
        user = User(
            name="Teacher Test",
            username="teacher_test",
            password=hashlib.md5("123456".encode("utf-8")).hexdigest(),
            email="teacher@test.com",
            role=UserEnum.TEACHER
        )
        db.session.add(user)
        db.session.commit()

        authenticated_user = auth_user("teacher_test", "123456")

        assert authenticated_user is not None
        assert authenticated_user.id == user.id
        assert authenticated_user.username == "teacher_test"


def test_auth_user_returns_none_with_invalid_password(app):
    with app.app_context():
        user = User(
            name="Student Test",
            username="student_test",
            password=hashlib.md5("correct-password".encode("utf-8")).hexdigest(),
            email="student@test.com",
            role=UserEnum.USER
        )
        db.session.add(user)
        db.session.commit()

        authenticated_user = auth_user("student_test", "wrong-password")

        assert authenticated_user is None
