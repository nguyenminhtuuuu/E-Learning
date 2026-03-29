import hashlib
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink
from flask_admin.model import InlineFormAdmin
from flask_admin.theme import Bootstrap4Theme
from flask_login import current_user
from backend.src import db, app
from backend.src.models import (Khoahoc, User, Lesson, Question, Answer, Enrollment)



class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self) -> str:
        if current_user.is_authenticated:
            return self.render('admin/index.html')
        return self.render('login.html')

class MyUserView(ModelView):
    column_list = ['id', 'username', 'email', 'role', 'active', 'created_date']
    column_searchable_list = ['username']
    column_filters = ['role']
    def on_model_change(self, form, model, is_created):
        if model.password:
            model.password = hashlib.md5(model.password.encode()).hexdigest()


class MyKhoahocView(ModelView):
    def _count_enrollments(view, context, model, name):
        return len(model.enrollments)

    column_list = ['id', 'name', 'Capdo', 'hocPhi', 'created_date', 'user', 'so_hoc_vien']
    column_searchable_list = ['name']
    column_filters = ['Capdo']
    column_labels = {
        'name': 'Tên khóa học',
        'Capdo': 'Cấp độ',
        'hocPhi': 'Học phí',
        'active': 'Trạng thái',
        'created_date': 'Ngày tạo',
        'user': 'Người tạo khóa học',
        'so_hoc_vien': 'Số học viên'
    }
    column_formatters = {
        'so_hoc_vien': _count_enrollments
    }

class MyLessonView(ModelView):
    column_list = ['id', 'title', 'content', 'khoahoc_id']
    column_searchable_list = ['title']
    column_filters = ['khoahoc_id']
    column_labels = {
        'title': 'Tiêu đề',
        'content': 'Nội dung',
        'khoahoc_id': 'Mã khóa học'
    }

class MyEnrollmentView(ModelView):
    column_list = ['id', 'user', 'khoahoc_enroll']
    column_labels = {
        'user': 'Học viên',
        'khoahoc_enroll': 'Khóa học',
    }
    column_searchable_list = ['user.name']

class AnswerInlineModel(InlineFormAdmin):
    form_columns = ['id', 'answer', 'is_correct']
    form_label = 'Answers'

class MyQuestionView(ModelView):
    column_list = ['id', 'content', 'khoahoc_id']
    column_labels = {
        'content': 'Nội dung',
        'khoahoc_id': 'Mã khóa học'
    }
    form_columns = ['content', 'khoahoc_id', 'answers']
    inline_models = (AnswerInlineModel(Answer),)


admin = Admin(app, name="E-Learning", theme=Bootstrap4Theme(), index_view=MyAdminIndexView())
admin.add_link(MenuLink(name='🏠 Trang chủ', url='/'))
admin.add_link(MenuLink(name='Đăng xuất', endpoint='logout_my_user'))


admin.add_view(MyUserView(User, db.session))
admin.add_view(MyKhoahocView(Khoahoc, db.session))
admin.add_view(MyLessonView(Lesson, db.session))
admin.add_view(MyEnrollmentView(Enrollment, db.session))
admin.add_view(MyQuestionView(Question, db.session))

