import pika


def create_connection(app):
    credentials = pika.PlainCredentials(
        app.config["RABBITMQ_USER"],
        app.config["RABBITMQ_PASS"]
    )
    parameters = pika.ConnectionParameters(
        host=app.config["RABBITMQ_HOST"],
        port=app.config["RABBITMQ_PORT"],
        credentials=credentials
    )
    return pika.BlockingConnection(parameters)


def declare_quiz_passed_queue(channel, app):
    channel.queue_declare(
        queue=app.config["RABBITMQ_QUEUE_QUIZ_PASSED"],
        durable=True
    )
