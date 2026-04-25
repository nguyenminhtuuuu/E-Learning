from backend.src.models import User, Khoahoc, Lesson, Progress, Capdo, UserEnum
from backend.src import db
from backend.src.dao import update_user_progress


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