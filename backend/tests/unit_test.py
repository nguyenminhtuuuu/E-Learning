import hashlib

from backend.src import db
from backend.src.dao import (add_user, auth_user, get_user_progress, is_course_completed, update_user_progress)
from backend.src.models import Capdo, Enrollment, Khoahoc, Lesson, Progress, User, UserEnum


def create_user_course_and_lessons(
    *,
    user_role=UserEnum.USER,
    username="test_user",
    email="test_user@test.com",
    lesson_count=1
):
    capdo = Capdo(name=f"Level-{username}")
    db.session.add(capdo)
    db.session.commit()

    user = User(
        name=f"User-{username}",
        username=username,
        password=hashlib.md5("123456".encode("utf-8")).hexdigest(),
        email=email,
        role=user_role
    )
    db.session.add(user)
    db.session.commit()

    khoahoc = Khoahoc(
        name=f"Course-{username}",
        capDo_id=capdo.id,
        hocPhi=100000,
        description="Course for testing",
        user_id=user.id
    )
    db.session.add(khoahoc)
    db.session.commit()

    lessons = []
    for index in range(lesson_count):
        lesson = Lesson(
            title=f"Lesson-{index + 1}-{username}",
            khoahoc_id=khoahoc.id
        )
        db.session.add(lesson)
        lessons.append(lesson)

    db.session.commit()
    return user, khoahoc, lessons


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


def test_update_user_progress_updates_existing_record_with_passing_score(app):
    with app.app_context():
        user, khoahoc, lessons = create_user_course_and_lessons(username="progress_update")
        progress = Progress(
            user_id=user.id,
            khoahoc_id=khoahoc.id,
            lesson_id=lessons[0].id,
            is_completed=False,
            score=0
        )
        db.session.add(progress)
        db.session.commit()

        update_user_progress(user.id, khoahoc.id, lessons[0].id, 8.5)

        updated_progress = Progress.query.filter_by(
            user_id=user.id,
            khoahoc_id=khoahoc.id,
            lesson_id=lessons[0].id
        ).first()

        assert updated_progress is not None
        assert updated_progress.is_completed is True
        assert updated_progress.score == 8.5


def test_update_user_progress_marks_quiz_incomplete_when_score_below_five(app):
    with app.app_context():
        user, khoahoc, lessons = create_user_course_and_lessons(username="progress_fail")

        update_user_progress(user.id, khoahoc.id, lessons[0].id, 4.5)

        progress = Progress.query.filter_by(
            user_id=user.id,
            khoahoc_id=khoahoc.id,
            lesson_id=lessons[0].id
        ).first()

        assert progress is not None
        assert progress.is_completed is False
        assert progress.score == 4.5


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


def test_add_user_hashes_password_before_saving(app):
    with app.app_context():
        add_user("New User", "new_user", "plain-password", "new_user@test.com", None)

        saved_user = User.query.filter_by(username="new_user").first()

        assert saved_user is not None
        assert saved_user.password == hashlib.md5("plain-password".encode("utf-8")).hexdigest()
        assert saved_user.password != "plain-password"


def test_is_course_completed_returns_true_when_lessons_and_quiz_are_done(app):
    with app.app_context():
        user, khoahoc, lessons = create_user_course_and_lessons(
            username="course_complete",
            lesson_count=2
        )

        for lesson in lessons:
            db.session.add(Progress(
                user_id=user.id,
                khoahoc_id=khoahoc.id,
                lesson_id=lesson.id,
                is_completed=True
            ))

        db.session.add(Progress(
            user_id=user.id,
            khoahoc_id=khoahoc.id,
            lesson_id=None,
            is_completed=True,
            score=9.0
        ))
        db.session.commit()

        assert is_course_completed(user.id, khoahoc.id) is True


def test_get_user_progress_returns_expected_percent(app):
    with app.app_context():
        user, khoahoc, lessons = create_user_course_and_lessons(
            username="progress_percent",
            lesson_count=2
        )
        db.session.add(Enrollment(user_id=user.id, khoahoc_id=khoahoc.id))
        db.session.add(Progress(
            user_id=user.id,
            khoahoc_id=khoahoc.id,
            lesson_id=lessons[0].id,
            is_completed=True
        ))
        db.session.add(Progress(
            user_id=user.id,
            khoahoc_id=khoahoc.id,
            lesson_id=None,
            is_completed=True,
            score=8.0
        ))
        db.session.commit()

        progress_data = get_user_progress(user.id)

        assert len(progress_data) == 1
        assert progress_data[0]["course_id"] == khoahoc.id
        assert progress_data[0]["completed"] == 1
        assert progress_data[0]["total"] == 2
        assert progress_data[0]["percent"] == 66



