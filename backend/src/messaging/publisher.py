import json
from datetime import datetime, timezone

import pika

from backend.src.messaging.events import QUIZ_PASSED_EVENT
from backend.src.messaging.rabbitmq import create_connection, declare_quiz_passed_queue


def publish_quiz_passed(app, user_id, course_id, lesson_id, score):
    payload = {
        "event_name": QUIZ_PASSED_EVENT,
        "user_id": user_id,
        "course_id": course_id,
        "lesson_id": lesson_id,
        "score": score,
        "completed_at": datetime.now(timezone.utc).isoformat()
    }

    connection = create_connection(app)
    try:
        channel = connection.channel()
        declare_quiz_passed_queue(channel, app)
        channel.basic_publish(
            exchange="",
            routing_key=app.config["RABBITMQ_QUEUE_QUIZ_PASSED"],
            body=json.dumps(payload),
            properties=pika.BasicProperties(delivery_mode=2)
        )
    finally:
        connection.close()

    return payload
