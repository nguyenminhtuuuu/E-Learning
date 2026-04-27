import json

from backend.src import app
from backend.src.messaging.rabbitmq import create_connection, declare_quiz_passed_queue


def start_consumer():
    connection = create_connection(app)
    channel = connection.channel()
    declare_quiz_passed_queue(channel, app)

    def callback(ch, method, properties, body):
        payload = json.loads(body.decode("utf-8"))
        user_id = payload.get("user_id")
        course_id = payload.get("course_id")
        lesson_id = payload.get("lesson_id")
        score = payload.get("score")
        completed_at = payload.get("completed_at")
        print(
            "[RabbitMQ] Event received:",
            f"event_name={payload.get('event_name')},",
            f"user_id={user_id},",
            f"course_id={course_id},",
            f"lesson_id={lesson_id},",
            f"score={score},",
            f"completed_at={completed_at}",
            flush=True
        )
        print(
            "[RabbitMQ] Mock notification processed:",
            f"to_user_id={user_id},",
            f"course_id={course_id},",
            f"lesson_id={lesson_id},",
            f"score={score},",
            "action=send_quiz_pass_notification",
            flush=True
        )
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue=app.config["RABBITMQ_QUEUE_QUIZ_PASSED"],
        on_message_callback=callback
    )

    print(
        f"[RabbitMQ] Waiting for messages on queue "
        f"'{app.config['RABBITMQ_QUEUE_QUIZ_PASSED']}'",
        flush=True
    )
    channel.start_consuming()
