from pstats import Stats

from flask import request
from flask_admin import Admin, BaseView, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from sqlalchemy.testing.suite.test_reflection import users
from models import SchoolRules, Notification, Role, Subject, Grade, Class
from StudentManager import app, db, dao
from flask_login import current_user


class AdminView(ModelView):
    can_view_details = True
    column_exclude_list = ['create_date', 'update_date']

    def is_accessible(self):
        if not current_user.is_authenticated or current_user.user_info.role != Role.ADMIN:
            return False
        return True


class BaseAdminView(ModelView):
    can_view_details = True
    column_exclude_list = ['create_date', 'update_date']

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_info.role == Role.ADMIN


class SchoolRulesView(BaseAdminView):
    column_searchable_list = ['min_age', 'max_age', 'max_students_in_class']
    column_labels = {
        'min_age': 'Tuổi tối thiểu',
        'max_age': 'Tuổi tối đa',
        'max_students_in_class': 'Số lượng học sinh tối đa',
        'active': 'Trạng thái'
    }


class NotificationView(BaseAdminView):
    column_filters = ['title', 'content']
    column_labels = {'content': 'Nội dung',
                     'title': 'Tiêu đề'}
    column_exclude_list = ['create_date', 'update_date', 'active']
    column_searchable_list = ['title', 'content']


class StatsView(BaseView):
    @expose('/')
    def index(self):
        grades = Grade
        subjects = Subject.query.all()
        classes = Class.query.all()

        selected_grade = request.args.get('grade')
        selected_subject = request.args.get('subject')
        selected_class = request.args.get('class')
        query = db.session.query(Class)

        if selected_grade:
            query = query.filter(Class.grade == selected_grade)

        if selected_subject:
            query = query.filter(Class.teaching_plan.any(Subject.id == selected_subject))

        if selected_class:
            query = query.filter(Class.id == selected_class)

        filtered_classes = query.all()

        return self.render('admin/stats.html', grades=grades, subjects=subjects, classes=classes,
                           filtered_classes=filtered_classes, selected_grade=selected_grade,
                           selected_subject=selected_subject, selected_class=selected_class)

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_info.role == Role.ADMIN


class SubjectView(BaseAdminView):
    column_labels = {'name': 'Tên môn học',
                     'desc': 'Mô tả',
                     'grade': 'Khối'}
    column_filters = ['name', 'grade']
    column_searchable_list = ['name', 'grade']


class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html')


admin = Admin(app=app, name="Quản trị viên", template_mode="bootstrap4", index_view=MyAdminIndexView())
admin.add_view(SchoolRulesView(SchoolRules, db.session, name="Quy định"))
admin.add_view(NotificationView(Notification, db.session, name="Thông báo"))
admin.add_view(SubjectView(Subject, db.session, name="Môn học"))
admin.add_view(StatsView(name='Thống kê'))
