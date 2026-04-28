import pika
import time


def create_connection(app):
    credentials = pika.PlainCredentials(
        app.config["RABBITMQ_USER"],
        app.config["RABBITMQ_PASS"]
    )
    host = app.config["RABBITMQ_HOST"]
    port = app.config["RABBITMQ_PORT"]
    parameters = pika.ConnectionParameters(host=host, port=port, credentials=credentials)

    max_attempts = 10
    for attempt in range(1, max_attempts + 1):
        try:
            return pika.BlockingConnection(parameters)
        except pika.exceptions.AMQPConnectionError:
            if attempt == max_attempts:
                raise
            print(
                f"[RabbitMQ] Connection failed for {host}:{port}; "
                f"retrying ({attempt}/{max_attempts})...",
                flush=True
            )
            time.sleep(3)


def declare_quiz_passed_queue(channel, app):
    channel.queue_declare(
        queue=app.config["RABBITMQ_QUEUE_QUIZ_PASSED"],
        durable=True
    )
