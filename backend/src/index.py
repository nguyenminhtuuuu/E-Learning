import re
import cloudinary
from flask import render_template, request, redirect, flash, url_for, jsonify
import math
from flask_login import login_user, current_user, logout_user, login_required
import cloudinary.uploader
from backend.src import dao, db, login, app


@app.route('/')
def index():
    q = request.args.get('q')
    capDo_id = request.args.get('capDo_id')
    page = request.args.get('page')
    khoahoc = dao.load_khoahoc(q=q, capDo_id=capDo_id, page=page)
    message = None
    if q and not khoahoc:
        message = f"Không tìm thấy khóa học! Vui lòng tìm kiếm khóa học khác!"
    pages = math.ceil(dao.count_khoahoc()/app.config["PAGE_SIZE"])

    return render_template('index.html', khoahoc=khoahoc, message=message, pages=pages)



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
            return redirect('/')
        else:
            flash("Tài khoản hoặc mật khẩu không đúng!", "danger")
            return redirect(url_for('login_my_user'))


    return render_template("login.html")

@app.context_processor #định danh biến toàn cục
def common_attribute():
    return {
        "capdo" : dao.load_capdo()
    }

@app.route("/logout")
def logout_my_user():
    logout_user()
    return redirect('/login')



@app.route("/register",  methods=['get', 'post'])
def register():
    err_msg = None

    if request.method.__eq__("POST"):
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        email = request.form.get('email')
        # import pdb #kiểm tra lỗi
        # pdb.set_trace()

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


@app.route("/admin-login", methods=["post"])
def login_admin_process():
    username = request.form.get("username")
    password = request.form.get("password")

    user = dao.auth_user(username, password)

    if user:
        login_user(user)
        return redirect("/admin")

    else:
        err_msg = "Tài khoản hoặc mật khẩu không đúng!"


# làm quiz
@app.route("/quiz/<int:khoahoc_id>", methods=['get', 'post'])
@login_required
def quiz(khoahoc_id):
    questions = dao.get_question_by_maKH(khoahoc_id)
    score = 0
    total = len(questions)
    result_score = 0
    show_results = False

    user_answer_id = {} # dictionary

    if request.method.__eq__("POST"):
        show_results = True
        for q in questions:
            ans = request.form.get(f'q_{q.id}')

            if ans:
                user_answer_id[q.id] = ans # { question_id : answer_id}
            correct_answer = dao.get_correct_answer(q.id)
            if ans and int(ans) == correct_answer.id:
                score += 1

        result_score = (score/total) * 10 if total > 0 else 0

    return render_template('quiz.html', questions=questions, result_score=result_score, score=score, total=total, show_results=show_results, user_answer_id=user_answer_id,khoahoc_id=khoahoc_id)



# # xem tiến độ học
# @app.route('/progress', methods=['get', 'post'])
# def progress():
#     return render_template('progress.html')
#
#
# # cấp chứng chỉ
# @app.route('certificate', methods=['get', 'post'])
# def certificate():
#     return render_template('certificate.html')


if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True,port=5000)
