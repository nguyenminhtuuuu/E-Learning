
import json
import hashlib

from click import Choice
from sqlalchemy import func, extract, case
from backend.src import db, app
from backend.src.models import (Capdo, Khoahoc, User, Question, Answer, Progress)
UserEnum = User.role.type.enum_class



def load_capdo():
    return Capdo.query.all()

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

def get_correct_answer(id):
    return Answer.query.filter_by(question_id=id, is_correct=True).first()

# xu ly tien do hoc
def get_user_progress(id):
    courses = Khoahoc.query.all()
    progress = []

    for c in courses:
        # tong so luong bai hoc va bai quiz
        # total_lessons = len(c.lessons)
        # moi khoa se co 1 bai quiz
        # total = total_lessons +1

        # count = Progress.query.filter_by(user_id=c.user_id, khoahoc_id=c.id, is_completed = True).count()
        #
        # percent = int((count/total)*100) if total > 0 else 0
        #
        # progress.append({
        #     'course_id' : c.id,
        #     'course_name' : c.name,
        #     'percent' : percent,
        #     'complete' : count,
        #     'total' : total
        # })

        return progress

if __name__ == '__main__':
    with app.app_context():
        print(count_khoahoc_by_capdo())
