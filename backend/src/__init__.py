# import cloudinary
# from flask_sqlalchemy import SQLAlchemy
# from flask_login import LoginManager
# from flask import Flask
#
# app = Flask(__name__)  # định vị vị trí của project hiện tại
# app.secret_key = "dshfuidsfjdshfjdh"
# app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:root@localhost/eldb?charset=utf8mb4"
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
# app.config["PAGE_SIZE"] = 8
# db = SQLAlchemy(app)
# cloudinary.config(cloud_name='deeqcwnpm',
#                   api_key='642514279843968',
#                   api_secret='iOM3oFrZpEwBIrnkHdaPfmT8njY',)
# login = LoginManager(app)

import os
import cloudinary
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login = LoginManager()


def create_app():
    # 2. Tính toán đường dẫn tương đối để tìm thư mục frontend
    src_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(src_dir, "..", ".."))

    template_dir = os.path.join(project_root, "frontend", "src", "templates")
    static_dir = os.path.join(project_root, "frontend", "src", "static")

    # 3. Khởi tạo App Flask duy nhất với cấu hình đường dẫn
    app = Flask(__name__,
                template_folder=template_dir,
                static_folder=static_dir)

    # 4. Cấu hình các thông số
    app.secret_key = "dshfuidsfjdshfjdh"
    db_host = os.environ.get("DB_HOST", "localhost")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://root:root@{db_host}/eldb?charset=utf8mb4"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
    app.config["PAGE_SIZE"] = 8
    app.config["RABBITMQ_HOST"] = os.environ.get("RABBITMQ_HOST", "localhost")
    app.config["RABBITMQ_PORT"] = int(os.environ.get("RABBITMQ_PORT", "5672"))
    app.config["RABBITMQ_USER"] = os.environ.get("RABBITMQ_USER", "guest")
    app.config["RABBITMQ_PASS"] = os.environ.get("RABBITMQ_PASS", "guest")
    app.config["RABBITMQ_QUEUE_QUIZ_PASSED"] = os.environ.get(
        "RABBITMQ_QUEUE_QUIZ_PASSED",
        "quiz_passed"
    )

    # 5. Cấu hình Cloudinary
    cloudinary.config(
        cloud_name='deeqcwnpm',
        api_key='642514279843968',
        api_secret='iOM3oFrZpEwBIrnkHdaPfmT8njY'
    )

    # 6. Gắn db và login vào App đã tạo
    db.init_app(app)
    login.init_app(app)

    #7. Khi login_required thì chuyển sang trang login
    login.login_view = 'login_my_user'

    return app

app = create_app()
