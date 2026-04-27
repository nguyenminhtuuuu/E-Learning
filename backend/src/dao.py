from pathlib import Path

from fpdf import FPDF
import os
import hashlib
from sqlalchemy import func
from backend.src import db, app
from backend.src.models import (Capdo, Khoahoc, User, Question, Answer, Progress, Lesson, Enrollment)
UserEnum = User.role.type.enum_class



def load_capdo():
    return Capdo.query.all()

#Khóa học

def load_khoahoc(q=None, id=None,capDo_id=None, page=None):
    query = Khoahoc.query
    if q:
        query = query.filter(Khoahoc.name.contains(q))

    if id:
        query = query.filter(Khoahoc.id.__eq__(id))

    if capDo_id:
        query = query.filter(Khoahoc.capDo_id == int(capDo_id))

    if page:
        size = app.config["PAGE_SIZE"]
        start = (int(page)-1)*size
        end = start + size
        query = query.slice(start, end)
    return query.all()

def load_khoahoc_by_user_id(user_id):
    return db.session.query(Khoahoc, func.count(Enrollment.id).label('so_luong')).outerjoin(Enrollment,
        Khoahoc.id == Enrollment.khoahoc_id).filter(Khoahoc.user_id==user_id).group_by(Khoahoc.id).all()

def get_khoahoc_by_id(id: None):
    return Khoahoc.query.filter(Khoahoc.id==id).first()


def get_registered_id(user):
    registered_id = []
    if user.is_authenticated:
        for e in user.enrollments:
            registered_id.append(e.khoahoc_id)
    return registered_id

# Lesson

def get_lesson_by_khoahoc(id: None):
    return Lesson.query.filter(Lesson.khoahoc_id==id).all()

def get_lesson_by_id(id: None):
    return Lesson.query.filter(Lesson.id==id).first()


def add_user(name,username, password, email, avatar):
    password = hashlib.md5(password.strip().encode("utf-8")).hexdigest()
    u = User(name=name, username=username.strip(), password=password, email=email.strip() if email else "",avatar=avatar)
    db.session.add(u)
    db.session.commit()



def get_khoahoc_by_maKH(id):
    return Khoahoc.query.get(id)



def auth_user(username, password):
    password= str(hashlib.md5(password.encode('utf-8')).hexdigest())
    return User.query.filter(User.username.__eq__(username), User.password.__eq__(password)).first()


def get_user_by_id(id):
    return User.query.get(id)

def count_khoahoc():
    return Khoahoc.query.count()


def count_khoahoc_by_capdo():
    query = db.session.query(Capdo.id, Capdo.name, func.count(Khoahoc.id)).join(Khoahoc, Khoahoc.capDo_id.__eq__(Capdo.id), isouter=True).group_by(Capdo.id)
    return query.all()


# xu ly quiz
def get_question_by_maKH(id):
    return Question.query.filter(Question.khoahoc_id == id).all()

def get_question_by_lesson(id):
    return Question.query.filter(Question.lesson_id == id).all()

def get_question_by_khoahoc(id):
    return Question.query.filter(Question.khoahoc_id==id).all()

def get_correct_answer(id):
    return Answer.query.filter_by(question_id=id, is_correct=True).first()

# xu ly tien do hoc
def update_user_progress(user_id, khoahoc_id, lesson_id = None, score = None):
    p = Progress.query.filter_by(user_id=user_id, khoahoc_id=khoahoc_id, lesson_id=lesson_id).first()

    if not p:
        p = Progress(user_id=user_id, khoahoc_id=khoahoc_id, lesson_id=lesson_id)
        db.session.add(p)

    if score is not None:
        p.score = score
        p.is_completed = (score >= 5.0)
    else:
        p.is_completed = True

    db.session.commit()


def is_course_completed(user_id, khoahoc_id):
    total_lessons = Lesson.query.filter_by(khoahoc_id=khoahoc_id).count()
    total_required = total_lessons + 1
    completed_items = Progress.query.filter_by(
        user_id=user_id,
        khoahoc_id=khoahoc_id,
        is_completed=True
    ).count()

    if total_required <= 0:
        return False

    return completed_items >= total_required

def get_user_progress(user_id, khoahoc_id = None, score=None):
    user_enrolls = Enrollment.query.filter_by(user_id=user_id).all()
    progress = []

    for u in  user_enrolls:
        c = Khoahoc.query.get(u.khoahoc_id)
        if c:
            # tong so luong bai hoc va bai quiz
            total_lessons = Lesson.query.filter_by(khoahoc_id=c.id).count()
            lessons_completed = Progress.query.filter_by(user_id=user_id, khoahoc_id=c.id,is_completed=True).filter(Progress.lesson_id.isnot(None)).count()
            # moi khoa se co 1 bai quiz
            total = total_lessons +1
            count = Progress.query.filter_by(user_id=user_id, khoahoc_id=c.id, is_completed = True).count()
            percent = int((count/total)*100) if total > 0 else 0
            progress.append({
                'course_id' : c.id,
                'course_name' : c.name,
                'course_image': c.image,
                'percent' : percent,
                'completed' : lessons_completed ,
                'total' : total_lessons
            })

    return progress

# xử lý chứng chỉ
def create_pdf_certificate(user_name, course_name):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()

    base_path = Path(__file__).parent
    font_path = base_path / "static" / "fonts" / "Arial.ttf"
    font_path_str = str(font_path.absolute())

    pdf.add_font("Arial-Unicode", style="", fname=font_path_str)
    pdf.set_font("Arial-Unicode", size=35)


    pdf.set_line_width(1.5)
    pdf.rect(10, 10, 277, 190)

    pdf.set_text_color(22, 43, 72)
    pdf.ln(20)
    pdf.cell(0, 20, 'CERTIFICATE OF COMPLETION', new_x="LMARGIN", new_y="NEXT", align='C')

    pdf.ln(20)
    pdf.set_font("Arial-Unicode", size=30)
    pdf.set_text_color(192, 57, 43)
    pdf.cell(0, 20, user_name.upper(), new_x="LMARGIN", new_y="NEXT", align='C')

    pdf.ln(10)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial-Unicode", size=20)
    pdf.cell(0, 10, f"Done: {course_name}", new_x="LMARGIN", new_y="NEXT", align='C')

    file_name = f"Cert_{user_name.replace(' ', '_')}.pdf"
    cert_dir = base_path / "static" / "certs"
    cert_dir.mkdir(parents=True, exist_ok=True)

    file_path = str(cert_dir / file_name)
    pdf.output(file_path)

    return file_path


# lay danh sach hoc vien
def get_user_enrolled(khoahoc_id):
    return db.session.query(User).join(Enrollment, User.id == Enrollment.user_id).filter(Enrollment.khoahoc_id==khoahoc_id).all()

if __name__ == '__main__':
    with app.app_context():
        print(count_khoahoc_by_capdo())
