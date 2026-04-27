from backend.src import app, dao
from backend.src.messaging.publisher import publish_quiz_passed


def mark_quiz_passed_and_publish(user_id, course_id, lesson_id, score):
    dao.update_user_progress(
        user_id=user_id,
        khoahoc_id=course_id,
        lesson_id=lesson_id,
        score=score
    )
    return publish_quiz_passed(app, user_id, course_id, lesson_id, score)
