from pstats import Stats

from flask import request, redirect, url_for, jsonify
from flask_admin import Admin, BaseView, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from sqlalchemy.testing.suite.test_reflection import users

from StudentManager.dao import get_years_semesters
from models import SchoolRules, Notification, Role, Subject, Grade, Class, Semester
from StudentManager import app, db, dao
from flask_login import current_user, logout_user


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
    can_create = False
    can_delete = False
    can_edit = True


class NotificationView(BaseAdminView):
    column_filters = ['title', 'content']
    column_labels = {'content': 'Nội dung',
                     'title': 'Tiêu đề'}
    column_exclude_list = ['create_date', 'update_date', 'active']
    column_searchable_list = ['title', 'content']


class StatsView(BaseView):
    @expose('/')
    def index(self):
        years = ["2024", "2025"]
        semesters = ["1", "2"]
        grades = [Grade.GRADE_10, Grade.GRADE_11, Grade.GRADE_12]

        selected_year = request.args.get('year', '2024')
        selected_semester = request.args.get('semester', '1')
        selected_subject = request.args.get('subject')
        selected_grade = request.args.get('grade')

        subjects = []

        if selected_grade:
            selected_grade = Grade(int(selected_grade))

        statistics = []
        statistics = dao.get_class_statistics(
            selected_year, selected_semester, selected_subject, selected_grade
        )

        print(
            f"Year: {selected_year}, Semester: {selected_semester}, Subject: {selected_subject}, Grade: {selected_grade}")
        print(dao.get_class_statistics(
            selected_year, selected_semester, selected_subject, selected_grade
        ))

        return self.render('admin/stats.html', years=years, selected_year=selected_year,
                           selected_semester=selected_semester, selected_subject=selected_subject,
                           selected_grade=selected_grade, grades=grades, subjects=subjects,
                           statistics=statistics)

    @expose('/get_subjects/<grade>', methods=['GET'])
    def get_subjects(self, grade):
        grade = Grade(int(grade))
        subjects = dao.get_subjects_by_grade(grade)
        if subjects:
            return jsonify([{"id": subject.id, "name": subject.name} for subject in subjects])

        return jsonify([])

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_info.role == Role.ADMIN


class SubjectView(BaseAdminView):
    column_labels = {'name': 'Tên môn học',
                     'desc': 'Mô tả',
                     'grade': 'Khối'}
    column_filters = ['name', 'grade']
    column_searchable_list = ['name', 'grade']


class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect(url_for('login_my_user'))


class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for('login_my_user'))
        statistics = []
        statistics = dao.get_class_statistics("2024", 1, 1, Grade.GRADE_10)

        return self.render('admin/index.html', statistics=statistics)


admin = Admin(app=app, name="Quản trị viên", template_mode="bootstrap4", index_view=MyAdminIndexView())
admin.add_view(SchoolRulesView(SchoolRules, db.session, name="Quy định"))
admin.add_view(NotificationView(Notification, db.session, name="Thông báo"))
admin.add_view(SubjectView(Subject, db.session, name="Môn học"))
admin.add_view(StatsView(name='Thống kê', endpoint='statsview'))
admin.add_view(LogoutView(name="Đăng xuất"))
