import re
import cloudinary
from flask import render_template, request, redirect, flash, url_for, jsonify, send_file
import math
from flask_login import login_user, current_user, logout_user, login_required
import cloudinary.uploader
from backend.src import dao, db, login, app, admin
from backend.src.models import Enrollment, Question, Khoahoc, Lesson, Answer
from backend.src.services.quiz_event_service import (
    mark_quiz_passed_and_publish,
)


@app.route('/')
def index():
    if current_user.is_authenticated and current_user.role.name == 'TEACHER':
        return redirect(url_for('teacher'))
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
            mark_quiz_passed_and_publish(
                user_id=current_user.id,
                course_id=khoahoc_id,
                lesson_id=lesson_id,
                score=result_score
            )

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
                           , registered_id=registered_id)


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


@app.route('/delete_khoahoc/<int:khoahoc_id>', methods=['POST'])
@login_required
def khoahoc_delete(khoahoc_id):
    khoahoc = db.session.get(Khoahoc, khoahoc_id)

    try:
        db.session.delete(khoahoc)
        db.session.commit()
        flash('Xóa thành công', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Xóa thất bại', 'danger')
        print(e)

    return redirect(url_for('khoahoc_manage'))


@app.route('/khoahoc_add')
@login_required
def khoahoc_add():
    return render_template('teacher/khoahoc_add.html')


@app.route('/add_khoahoc', methods=['POST'])
@login_required
def add_khoahoc():
    khoahoc_name = request.form['khoahoc_name']
    capdo_id = request.form['capdo_id']
    khoahoc_hp = request.form['khoahoc_hp']
    text = request.form['khoahoc_text']

    file = request.files.get('ten_file')
    image_url = None

    if file and file.filename != "":
        upload_result = cloudinary.uploader.upload(file)
        image_url = upload_result['secure_url']

    k = Khoahoc(
        name=khoahoc_name,
        capDo_id=capdo_id,
        hocPhi=khoahoc_hp,
        description=text,
        image=image_url,
        user_id=current_user.id
    )
    db.session.add(k)
    db.session.commit()
    return redirect(url_for('khoahoc_manage'))


@app.route('/khoahoc_update/<int:khoahoc_id>')
@login_required
def khoahoc_update(khoahoc_id):
    k = dao.get_khoahoc_by_id(khoahoc_id)
    return render_template('teacher/khoahoc_update.html', k=k)


@app.route('/update_khoahoc/<int:khoahoc_id>', methods=['POST'])
@login_required
def update_khoahoc(khoahoc_id):
    k = Khoahoc.query.get(khoahoc_id)
    k.name = request.form['khoahoc_name']
    k.capDo_id = request.form['capdo_id']
    k.hocPhi = request.form['khoahoc_hp']
    k.description = request.form['khoahoc_text']

    file = request.files.get('ten_file')
    if file and file.filename != "":
        upload_result = cloudinary.uploader.upload(file)
        k.image = upload_result['secure_url']

    db.session.commit()
    return redirect(url_for('khoahoc_manage'))


# Quan ly lesson
@app.route('/delete_lesson/<int:lesson_id>', methods=['POST'])
@login_required
def lesson_delete(lesson_id):
    lesson = db.session.get(Lesson, lesson_id)

    try:
        db.session.delete(lesson)
        db.session.commit()
        flash('Xóa thành công', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Xóa thất bại', 'danger')
        print(e)

    return redirect(url_for('khoahoc_manage'))


@app.route('/lesson_add/<int:khoahoc_id>')
@login_required
def lesson_add(khoahoc_id):
    k = dao.get_khoahoc_by_id(khoahoc_id)
    return render_template('teacher/lesson_add.html', k=k)


@app.route('/add_lesson/<int:khoahoc_id>', methods=['POST'])
@login_required
def add_lesson(khoahoc_id):
    lesson_name = request.form['lesson_name']
    lesson_text = request.form['lesson_text']

    video_url = None
    file = request.files.get('ten_file')
    if file and file.filename != "":
        try:
            upload_result = cloudinary.uploader.upload(file, resource_type="video")
            video_url = upload_result.get('secure_url')
        except Exception as e:
            print("Upload lỗi:", e)
            video_url = None

    lesson = Lesson(
        khoahoc_id=khoahoc_id,
        title=lesson_name,
        video_url=video_url,
        content=lesson_text
    )
    db.session.add(lesson)
    db.session.commit()
    return redirect(url_for('khoahoc_manage'))


@app.route('/lesson_update/<int:lesson_id>')
@login_required
def lesson_update(lesson_id):
    lesson = dao.get_lesson_by_id(lesson_id)
    return render_template('teacher/lesson_update.html', lesson=lesson)


@app.route('/update_lesson/<int:lesson_id>', methods=['POST'])
@login_required
def update_lesson(lesson_id):
    lesson = Lesson.query.get(lesson_id)
    lesson.title = request.form['lesson_name']
    lesson.content = request.form['lesson_text']

    file = request.files.get('ten_file')
    delete_video = request.form.get('delete_video')

    if delete_video and lesson.video_url:
        lesson.video_url = None

    if file and file.filename != "":
        upload_result = cloudinary.uploader.upload(file, resource_type="video")
        lesson.video_url = upload_result['secure_url']

    db.session.commit()
    return redirect(url_for('khoahoc_manage'))


# Câu hỏi

@app.route('/question_manage/<int:lesson_id>')
def question_manage(lesson_id):
    questions = dao.get_question_by_lesson(lesson_id)
    return render_template('teacher/question_manage.html', lesson_id=lesson_id, questions=questions)


@app.route('/question_add/<int:lesson_id>')
def question_add(lesson_id):
    return render_template('teacher/question_add.html', lesson_id=lesson_id)


@app.route('/add_question/<int:lesson_id>', methods=['GET', 'POST'])
def add_question(lesson_id):
    if request.method == 'POST':
        content = request.form.get('content')
        a1 = request.form.get('a1')
        a2 = request.form.get('a2')
        correct = request.form.get('correct')

        l = dao.get_lesson_by_id(lesson_id)
        q = Question(
            content=content,
            lesson_id=lesson_id,
            khoahoc_id=l.khoahoc_id
        )

        db.session.add(q)
        db.session.commit()

        db.session.add(Answer(
            answer=a1,
            is_correct=(correct == '1'),
            question_id=q.id
        ))
        db.session.add(Answer(
            answer=a2,
            is_correct=(correct == '2'),
            question_id=q.id
        ))

        db.session.commit()
        return redirect(url_for('question_manage', lesson_id=lesson_id))
    return render_template('teacher/question_add.html',  lesson_id=lesson_id)


@app.route('/update_questions/<int:lesson_id>', methods=['POST'])
def update_all_questions(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)

    for q in lesson.questions:
        q.content = request.form.get(f'question_{q.id}')

        for a in q.answers:
            a.answer = request.form.get(f'answer_{a.id}')

        correct_id = request.form.get(f'correct_{q.id}')
        if correct_id:
            correct_id = int(correct_id)
            for a in q.answers:
                a.is_correct = (a.id == correct_id)

    db.session.commit()

    return redirect(url_for('question_manage', lesson_id=lesson_id))


@app.route('/delete_question/<int:question_id>', methods=['POST'])
def question_delete(question_id):
    q = db.session.get(Question, question_id)

    try:
        db.session.delete(q)
        db.session.commit()
        flash('Xóa thành công', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Xóa thất bại', 'danger')
        print(e)

    return redirect(url_for('question_manage',lesson_id=q.lesson_id))

if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True, port=5000)
