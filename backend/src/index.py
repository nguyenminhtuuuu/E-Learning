import re
import cloudinary
from flask import render_template, request, redirect, flash, url_for, jsonify, send_file
import math
from flask_login import login_user, current_user, logout_user, login_required
import cloudinary.uploader
from backend.src import dao, db, login, app, admin
from backend.src.models import Enrollment, Question, Khoahoc


@app.route('/')
def index():
    if current_user.is_authenticated and current_user.role.name == 'TEACHER':
        return redirect(url_for('teacher'))
    if current_user.is_authenticated and current_user.role.name == 'ADMIN':
        return redirect(url_for('admin.index'))
    q = request.args.get('q')
    capDo_id = request.args.get('capDo_id')
    page = request.args.get('page')
    khoahoc = dao.load_khoahoc(q=q, capDo_id=capDo_id, page=page)
    message = None
    if q and not khoahoc:
        message = f"Không tìm thấy khóa học! Vui lòng tìm kiếm khóa học khác!"
    pages = math.ceil(dao.count_khoahoc() / app.config["PAGE_SIZE"])

    registered_id = dao.get_registered_id(current_user)
    return render_template('index.html', khoahoc=khoahoc, message=message, pages=pages, registered_id=registered_id)


@app.route("/login", methods=['get', 'post'])
def login_my_user():
    if current_user.is_authenticated:
        return redirect('/')

    err_msg = None
    if request.method.__eq__('POST'):
        username = request.form.get("username")
        password = request.form.get("password")

        user = dao.auth_user(username, password)

        if user:
            login_user(user)
            if user.role.name == 'ADMIN':
                return redirect(url_for('admin.index'))
            elif user.role.name == 'TEACHER':
                return redirect(url_for('teacher'))
            return redirect('/')

        else:
            flash("Tài khoản hoặc mật khẩu không đúng!", "danger")
            return redirect(url_for('login_my_user'))

    return render_template("login.html")


@app.context_processor  # định danh biến toàn cục
def common_attribute():
    return {
        "capdo": dao.load_capdo()
    }


@app.route("/logout")
def logout_my_user():
    logout_user()
    return redirect('/login')


@app.route("/register", methods=['get', 'post'])
def register():
    err_msg = None

    if request.method.__eq__("POST"):
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        email = request.form.get('email')

        if not password.__eq__(confirm):
            err_msg = "Mật khẩu không khớp!"
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            err_msg = "Định dạng email không hợp lệ!"
        else:
            name = request.form.get("name")
            username = request.form.get("username")
            avatar = request.files.get("avatar")
            path_file = None
            if avatar:
                res = cloudinary.uploader.upload(avatar)
                path_file = res["secure_url"]
            try:
                dao.add_user(name, username, password, email, avatar=path_file)
                return redirect('/login')
            except:
                db.session.rollback()
                err_msg = "Hệ thống đang có lỗi! Vui lòng quay lại sau!"

    return render_template("register.html", err_msg=err_msg)


@login.user_loader
def get_user(user_id):
    return dao.get_user_by_id(user_id)


# Endpoints

@app.route("/admin")
def login_admin_process():
    return redirect(url_for('admin.index'))


# @app.route("/teacher")
# def login_teacher():
#     q = request.args.get('q')
#     capDo_id = request.args.get('capDo_id')
#     page = request.args.get('page')
#     khoahoc = dao.load_khoahoc(q=q, capDo_id=capDo_id, page=page)
#     message = None
#     if q and not khoahoc:
#         message = f"Không tìm thấy khóa học! Vui lòng tìm kiếm khóa học khác!"
#     pages = math.ceil(dao.count_khoahoc() / app.config["PAGE_SIZE"])
#
#     registered_id = dao.get_registered_id(current_user)
#     return render_template('teacher/index.html', khoahoc=khoahoc, message=message, pages=pages, registered_id=registered_id)

# Lesson
@app.route('/lesson/<int:khoahoc_id>')
def lesson(khoahoc_id):
    lessons = dao.get_lesson_by_khoahoc(khoahoc_id)
    message = None
    is_registered = False
    if current_user.is_authenticated:
        registered_id = dao.get_registered_id(current_user)
        if khoahoc_id in registered_id:
            is_registered = True
    if not lessons:
        message = f"Khóa học chưa có bài học!"
    khoahoc = dao.get_khoahoc_by_id(khoahoc_id)
    return render_template('lesson.html', lessons=lessons, khoahoc=khoahoc, message=message,
                           is_registered=is_registered)


@app.route('/lesson_detail/<int:lesson_id>')
@login_required
def lesson_detail(lesson_id):
    is_registered = False
    lesson = dao.get_lesson_by_id(lesson_id)
    register = dao.get_registered_id(current_user)
    if lesson.khoahoc_id in register:
        is_registered = True
    message = f"Bạn chưa đăng ký khóa học này!!"
    dao.update_user_progress(user_id=current_user.id, khoahoc_id=lesson.khoahoc_id, lesson_id=lesson_id)
    return render_template('lesson_detail.html', lesson=lesson, is_registered=is_registered, message=message)


@app.route('/dangky/<int:khoahoc_id>', methods=['POST'])
@login_required
def dangky(khoahoc_id):
    e = Enrollment.query.filter_by(user_id=current_user.id, khoahoc_id=khoahoc_id).first()

    if not e:
        e = Enrollment(
            user_id=current_user.id,
            khoahoc_id=khoahoc_id
        )
        db.session.add(e)
        db.session.commit()

    return redirect(url_for('index'))


# làm quiz
@app.route("/quiz/<int:khoahoc_id>", methods=['get', 'post'])
@app.route("/quiz/lesson/<int:lesson_id>", methods=['get', 'post'])
@login_required
def quiz(khoahoc_id=None, lesson_id=None):
    questions = []

    if lesson_id:
        questions = dao.get_question_by_lesson(lesson_id)

        lesson_obj = dao.get_lesson_by_id(lesson_id)
        khoahoc_id = lesson_obj.khoahoc_id

    else:
        questions = dao.get_question_by_maKH(khoahoc_id)

    score = 0
    total = len(questions)
    result_score = 0
    show_results = False

    user_answer_id = {}  # dictionary

    if request.method.__eq__("POST"):
        show_results = True
        for q in questions:
            ans = request.form.get(f'q_{q.id}')

            if ans:
                user_answer_id[q.id] = ans  # { question_id : answer_id}
            correct_answer = dao.get_correct_answer(q.id)
            if ans and int(ans) == correct_answer.id:
                score += 1

        result_score = (score / total) * 10 if total > 0 else 0

        if result_score >= 5:
            dao.update_user_progress(user_id=current_user.id, khoahoc_id=khoahoc_id, lesson_id=lesson_id,
                                     score=result_score)

    return render_template('quiz.html', questions=questions, result_score=result_score, score=score, total=total,
                           show_results=show_results, user_answer_id=user_answer_id, khoahoc_id=khoahoc_id,
                           lesson_id=lesson_id)


# xem tiến độ học
@app.route('/progress', methods=['get', 'post'])
@login_required
def progress():
    progress = dao.get_user_progress(current_user.id)
    return render_template('progress.html', progress_data=progress, is_teacher_view=False)


# cấp chứng chỉ
@app.route('/certificate/<int:khoahoc_id>', methods=['get', 'post'])
def certificate(khoahoc_id):
    progress = dao.get_user_progress(current_user.id)
    course_progress = next((item for item in progress if item['course_id'] == khoahoc_id), None)

    if course_progress and course_progress['percent'] == 100:
        file_path = dao.create_pdf_certificate(current_user.name, course_progress['course_name'])
        return send_file(file_path, as_attachment=True)
    return redirect('/')


# giao vien
@app.route('/teacher')
@login_required
def teacher():
    q = request.args.get('q')
    capDo_id = request.args.get('capDo_id')
    page = request.args.get('page')
    khoahoc = dao.load_khoahoc(q=q, capDo_id=capDo_id, page=page)
    message = None
    if q and not khoahoc:
        message = f"Không tìm thấy khóa học! Vui lòng tìm kiếm khóa học khác!"
    pages = math.ceil(dao.count_khoahoc() / app.config["PAGE_SIZE"])

    registered_id = dao.get_registered_id(current_user)
    return render_template('teacher/teacher.html', q=q, pages=pages, khoahoc=khoahoc, message=message
                           , registered_id = registered_id)

@app.route('/teacher-progress')
@login_required
def teacher_progress():
    khoahoc = dao.load_khoahoc_by_user_id(current_user.id)
    return render_template('teacher/teacher_progress.html', khoahoc=khoahoc)

@app.route('/teacher-progress-detail/<int:khoahoc_id>')
@login_required
def teacher_progress_detail(khoahoc_id):
    user = dao.get_user_enrolled(khoahoc_id)
    message = None
    if not user:
        message = f'Chưa có sinh viên đăng ký khoá học này'
    return render_template('teacher/teacher_progress_detail.html', user=user, message=message)

@app.route('/teacher/view-progress/<int:user_id>')
@login_required
def teacher_view_progress(user_id):
    progress_data = dao.get_user_progress(user_id)
    return render_template('progress.html', progress_data=progress_data, is_teacher_view=True)

@app.route('/khoahoc_manage')
@login_required
def khoahoc_manage():
    khoahoc = dao.load_khoahoc_by_user_id(current_user.id)
    return render_template('teacher/khoahoc_manage.html', khoahoc=khoahoc)

@app.route('/delete/<int:khoahoc_id>', methods=['POST'])
@login_required
def khoahoc_delete(khoahoc_id):
    khoahoc = db.session.get(Khoahoc, khoahoc_id)

    try:
        db.session.delete(khoahoc)
        db.session.commit()
        flash('Xóa thành công','success')
    except Exception as e:
        db.session.rollback()
        flash('Xóa thất bại', 'danger')
        print(e)

    return redirect(url_for('khoahoc_manage'))

@app.route('/khoahoc_add')
def khoahoc_add():
    return render_template('teacher/khoahoc_add.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['ten_file']
    result = cloudinary.uploader.upload(file)
    return {
        "url": result['secure_url']
    }

# @app.route('add_khoahoc', methods=['POST'])
# def add_khoahoc():
#     khoahoc_name = request.form['khoahoc_name']
#     khoahoc_hp= request.form['khoahoc_hp']
#     text = request.form['khoahoc_text']
#     hinh_anh = request.files['ten_file']
#     k = Khoahoc(
#         name=khoahoc_name,
#         khoahoc_hp=khoahoc_hp,
#         text=text,
#         hinh_anh=hinh_anh
#     )

if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True, port=5000)
