import math
import re
from datetime import date
from email.policy import default
from mmap import PAGESIZE
from turtledemo.penrose import start

from flask_admin.model.typefmt import null_formatter

import dao
import cloudinary.uploader
from flask import render_template, request, redirect, session, jsonify, flash, url_for
from flask_login import login_user, current_user, logout_user
from datetime import datetime
from StudentManager import app, login, admin
from models import *


# index
@app.route('/', methods=['GET'])
def index():
    if current_user.is_authenticated:
        page = request.args.get('page', 1)
        page = int(page)
        pages = dao.count_notifications()
        notifications = dao.get_all_notifications()
        return render_template('index.html', pages=math.ceil(pages / app.config["NOTIFICATIONS_PAGE_SIZE"]),
                               current_page=int(page),
                               notifications=notifications)
    return redirect('/login')


# ##################################### STUDENT ###################################################

# student_admission
@app.route('/students', methods=['get', 'post'])
def student_management():
    page = request.args.get('page', 1, type=int)
    students_paginated = dao.get_all_students(page)
    grades = Grade.choices()

    total_pages = students_paginated.pages
    max_pages_display = 10

    start_page = max(1, page - max_pages_display // 2)
    end_page = min(total_pages, start_page + max_pages_display - 1)

    if end_page - start_page + 1 < max_pages_display:
        start_page = max(1, end_page - max_pages_display + 1)

    return render_template('/employee/student_management.html',
                           students=students_paginated.items,
                           grades=grades,
                           pagination=students_paginated,
                           total_pages = total_pages,
                           start_page=start_page,
                           end_page=end_page)


# student details
@app.route('/students/<int:student_id>')
def student_details(student_id):
    student = dao.get_student_by_id(student_id)
    student_info = dao.get_user_info_by_id(student_id)

    cls = dao.get_class_by_id(student.class_id)
    class_name = None
    if cls:
        class_name = cls.name

    return render_template('/employee/student_details.html', student=student, student_info=student_info, class_name=class_name)


@app.route('/get_students', methods=['POST'])
def get_students():
    class_id = request.json.get('classId')
    students = dao.get_students_by_class(class_id)
    return jsonify({"students": students})


@app.route('/api/students', methods=['POST'])
def add_student():
    data = request.get_json()

    if not data:
        flash("Có lỗi xảy ra!", "danger")
        return jsonify({"success": False}), 400

    name = data.get('name')
    gender = True if data.get('gender') == "Male" else False
    date_of_birth = data.get('date_of_birth')
    dob = datetime.strptime(date_of_birth, '%Y-%m-%d') if date_of_birth else None
    address = data.get('address')
    phone = data.get('phone')
    email = data.get('email')
    grade_value = data.get('grade')

    if not name or not date_of_birth or not address or not phone or not email or not grade_value:
        flash("Vui lòng nhập đầy đủ thông tin!", "danger")
        return jsonify({"success": False}), 400

    if dao.check_phone_unique(phone) is False:
        flash("Số điện thoại đã tồn tại!", "danger")
        return jsonify({"success": False}), 400

    if dao.check_email_unique(email) is False:
        flash("Địa chỉ email đã tồn tại!", "danger")
        return jsonify({"success": False}), 400

    if not is_valid_phone(phone):
        flash("Số điện thoại phải có 10 hoặc 11 chữ số!", "danger")
        return jsonify({"success": False}), 400

    age_validation = is_valid_age(dob)
    if age_validation is not True:
        flash(age_validation, "danger")
        return jsonify({"success": False}), 400

    try:
        new_user_info = UserInformation(
            full_name=name,
            gender=gender,
            address=address,
            birth=dob,
            phone=phone,
            email=email,
            role=Role.STUDENT
        )
        db.session.add(new_user_info)
        db.session.commit()

        grade = Grade(int(grade_value))
        cls = dao.get_class_by_grade(grade)
        print(cls)

        if cls:
            new_student = Student(id=new_user_info.id, grade=grade, class_id=cls.id)
        else:
            new_student = Student(id=new_user_info.id, grade=grade)

        db.session.add(new_student)
        db.session.commit()

        flash("Thêm học sinh thành công!", "success")
        return jsonify({"success": True}), 201

    except Exception as e:
        db.session.rollback()
        flash(f"Đã có lỗi xảy ra: {str(e)}", "danger")
        return jsonify({"success": False}), 500


@app.route('/api/students/delete/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    student = Student.query.get(student_id)
    print(student)
    if student:
        student.active = False
        db.session.commit()
        flash("Xoá thành công!", "success")
        return jsonify({"success": True})
    else:
        flash("Xoá thất bại!", "danger")
        return jsonify({"success": False})


def is_valid_phone(phone):
    return bool(re.match(r'^0\d{9,10}$', phone))


def is_valid_age(birthdate):
    today = datetime.today()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

    rule = SchoolRules.query.order_by(SchoolRules.id.desc()).first()
    if rule:
        min_age = rule.min_age
        max_age = rule.max_age
    else:
        min_age = 15
        max_age = 20

    if not (min_age <= age <= max_age):
        return f"Tuổi phải trong độ tuổi quy định ( {min_age} - {max_age} )"

    return True


# ##################################### CLASS ###################################################

# class_management
@app.route('/classes', methods=['get', 'post'])
def class_management():
    page = request.args.get('page', 1)
    page = int(page)
    pages = dao.count_classes()
    classes = dao.get_all_classes(page)
    return render_template("/employee/class_management.html",
                           classes=classes,
                           pages=math.ceil(pages / app.config["CLASSES_PAGE_SIZE"]),
                           current_page=int(page),
                           total_classes=pages)


# class details
@app.route('/classes/<int:class_id>')
def class_details(class_id):
    cls = dao.get_class_by_id(class_id)
    amount = dao.count_students_in_class(cls.id)

    page = request.args.get('page', 1, type=int)
    pages = dao.count_students_in_class(cls.id)
    students = dao.get_students_by_class(cls.id, page)

    print(math.ceil(pages / app.config["PAGE_SIZE"]))

    return render_template('/employee/class_details.html',
                           cls=cls,
                           amount=amount,
                           students=students,
                           pages=math.ceil(pages / app.config["PAGE_SIZE"]),
                           current_page=int(page))


@app.route('/get_classes/<grade>', methods=['GET'])
def get_classes(grade):
    grade = Grade(int(grade))
    classes = dao.get_classes_by_grade(grade)
    if classes:
        return jsonify([{"id": cls.id, "name": cls.name} for cls in classes])

    return jsonify([])


# api add class
@app.route('/api/classes', methods=['post'])
def add_class():
    class_name = request.json.get('class_name')
    grade_value = request.json.get('grade')

    # chuyển giá trị lấy được sang enum
    grade = Grade(int(grade_value))

    if Class.query.filter_by(name=class_name, grade=grade, active=True).first():
        flash("Lớp đã tồn tại!", "danger")
        return jsonify({"success": False})

    new_class = Class(name=class_name, grade=grade)

    # Thêm vào database
    db.session.add(new_class)
    db.session.commit()

    flash("Thêm lớp thành công!", "success")
    return jsonify({"success": True})


# api delete class
@app.route('/api/classes/delete/<int:class_id>', methods=['POST'])
def delete_class(class_id):
    cls = dao.get_class_by_id(class_id)
    if cls:
        cls.active = False
        db.session.commit()
        flash("Xoá thành công!", "success")
        return jsonify({"success": True})
    else:
        flash("Xoá thất bại!", "danger")
        return jsonify({"success": False})


# ##################################### SUBJECT ###################################################

# subject
@app.route('/subjects')
def subject_management():
    page = request.args.get('page', 1)
    page = int(page)
    pages = dao.count_subjects()
    subjects = dao.get_all_subjects(page)
    return render_template('/employee/subject_management.html',
                           subjects=subjects,
                           pages=math.ceil(pages / app.config["SUBJECTS_PAGE_SIZE"]),
                           current_page=int(page),
                           total_subjects=pages)


@app.route('/get_subjects/<grade>', methods=['GET'])
def get_subjects(grade):
    grade = Grade(int(grade))
    subjects = dao.get_subjects_by_grade(grade)
    if subjects:
        return jsonify([{"id": subject.id, "name": subject.name} for subject in subjects])

    return jsonify([])


@app.route('/api/subjects', methods=['post'])
def add_subjects():
    subject_name = request.json.get('subject_name')
    desc = request.json.get('desc')
    if not desc:
        desc = ""
    grade_value = request.json.get('grade')

    # chuyển giá trị lấy được sang enum
    grade = Grade(int(grade_value))

    if Subject.query.filter_by(name=subject_name, grade=grade, active=True).first():
        flash("Môn học đã tồn tại!", "danger")
        return jsonify({"success": False})

    new_subject = Subject(name=subject_name, desc=desc, grade=grade)

    # Thêm vào database
    db.session.add(new_subject)
    db.session.commit()

    flash("Thêm môn học thành công!", "success")
    return jsonify({"success": True})


@app.route('/api/subjects/delete/<int:subject_id>', methods=['POST'])
def delete_subject(subject_id):
    subject = dao.get_subject_by_id(subject_id)
    if subject:
        subject.active = False
        db.session.commit()
        flash("Xoá thành công!", "success")
        return jsonify({"success": True})
    else:
        flash("Xoá thất bại!", "danger")
        return jsonify({"success": False})


# ##################################### RULE ###################################################

@app.route('/rules')
def rules():
    return render_template('/admin/rules.html')


# ##################################### STATS ###################################################

@app.route('/stats')
def stats():
    return render_template('/admin/stats.html')


# ##################################### LOGIN - REGISTER ###################################################

# register
@app.route('/register', methods=["get", "post"])
def register_user():
    err_msg = None
    if request.method.__eq__('POST'):
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        if password.__eq__(confirm):
            ava_path = None
            name = request.form.get('name')
            username = request.form.get('username')
            avatar = request.files.get('avatar')
            if avatar:
                res = cloudinary.uploader.upload(avatar)
                ava_path = res['secure_url']
            dao.add_user(name=name, username=username, password=password, avatar=ava_path)
            return redirect('/login')
        else:
            err_msg = "Mật khẩu không khớp!"
    return render_template('register.html', err_msg=err_msg)


# login
@app.route('/login', methods=['get', 'post'])
def login_my_user():
    if current_user.is_authenticated:
        return redirect('/')
    err_msg = None
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        user = dao.auth_user(username=username, password=password)
        if user:
            login_user(user)
            if user.user_info.role == Role.ADMIN:
                return redirect('/admin/')
            return redirect('/')
        else:
            err_msg = "Tài khoản hoặc mật khẩu không đúng!"

    return render_template('login.html', err_msg=err_msg)


@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id=user_id)


# logout
@app.route('/logout')
def logout_my_user():
    logout_user()
    return redirect('/login')


# ##################################### PROFILE ###################################################

# employee_profile
@app.route('/profile')
def employee_profile():
    user = dao.get_user_by_id(current_user.get_id())
    return render_template('/employee/employee_profile.html', username=user.username)


# ##################################### SCORE ###################################################
@app.route('/entry_score')
def entry_score():
    subjects = dao.get_all_subjects()
    return render_template('/lecturer/entry_score.html',
                           subjects=subjects)


@app.route('/get_exam_quantities/<int:subject_id>', methods=['GET'])
def get_exam_quantities(subject_id):
    exam_quantities = dao.get_lastest_exam_quantities(subject_id)
    return jsonify(exam_quantities)


@app.route('/save_scores', methods=['POST'])
def save_scores():
    try:
        class_id = request.json.get('classId')
        subject_id = request.json.get('subjectId')
        scores = request.json.get('scores')

        semester_value = request.json.get('semester')
        semester = dao.get_semester(semester_value)

        teaching_plan = dao.get_teaching_plan(class_id, subject_id, semester.id, current_user.get_id())

        for score_data in scores:
            student_id = score_data.get('studentId')
            score_type = score_data.get('scoreType')
            score_value = score_data.get('score')
            index = score_data.get('index')

            dao.save_score(student_id, teaching_plan.id, score_type, score_value, index)

        return jsonify({'success': True, 'message': 'Lưu điểm thành công!'})

    except Exception as e:
        print(f"Lỗi: {e}")
        return jsonify({'error': 'Đã xảy ra lỗi!'})


@app.route('/get_scores', methods=['POST'])
def get_scores():
    student_ids = request.json.get('student_ids', [])
    subject_id = request.json.get('subjectId')
    semester_value = request.json.get('semester')
    class_id = request.json.get('classId')

    semester = dao.get_semester(semester_value)
    scores = dao.get_scores_by_subject_and_semester(student_ids, subject_id, semester.id, class_id,
                                                    current_user.get_id())

    result = {}
    for student_id in student_ids:
        student_scores = [score for score in scores if score.student_id == student_id]

        scores_by_type = {
            score_type.name: [] for score_type in ScoreType
        }

        for score in student_scores:
            score_type = score.score_type.name
            scores_by_type[score_type].append(score.score)

        result[str(student_id)] = scores_by_type

    return jsonify(result)


@app.route('/export_score')
def export_score():
    return render_template('/lecturer/export_score.html')


@app.route('/get_avg_scores', methods=['POST'])
def get_avg_scores():
    students = request.json.get('students', [])
    subjects = request.json.get('subjects')
    semester_value = request.json.get('semester')
    class_id = request.json.get('classId')

    if int(semester_value) == 3:
        year = date.today().year
        semesters = dao.get_semesters_by_year(year)
    else:
        semester = dao.get_semester(semester_value)
        semesters = [semester]

    averages = {}

    for subject_id in subjects:
        scores = []
        for semester in semesters:
            scores += dao.get_scores_by_subject_and_semester(students, subject_id, semester.id, class_id,
                                                             current_user.get_id())

        # Tạo obj lưu điểm theo hs
        scores_by_student = {}
        for score in scores:
            student_id = score.student_id
            if student_id not in scores_by_student:
                scores_by_student[student_id] = []
            scores_by_student[student_id].append(score.score)

        # Tính điểm trung bình
        for student_id, scores_list in scores_by_student.items():
            avg_score = sum(scores_list) / len(scores_list) if scores_list else 0

            # Thêm kết quả vào cấu trúc
            if student_id not in averages:
                averages[student_id] = {"subjects": {}, "overall_average": 0}
            averages[student_id]["subjects"][subject_id] = {
                "average": round(avg_score, 2)
            }

    # Tính điểm trung bình tất cả các môn
    for student_id, data in averages.items():
        subject_averages = [subject["average"] for subject in data["subjects"].values()]
        overall_avg = sum(subject_averages) / len(subject_averages) if subject_averages else 0
        data["overall_average"] = round(overall_avg, 2)

    # "averages": {
    #     "student_id": {
    #         "subjects": {
    #             "subject_id": {
    #                 "average": 8.3
    #             },
    #             "subject_id": {
    #                 "average": 9.1
    #             }
    #         },
    #         "overall_average": 8.7

    return jsonify(averages)


@app.context_processor
def common_attributes():
    if current_user.is_authenticated:
        return {
            "user_info": dao.get_user_info_by_user_id(user_id=current_user.get_id())
        }

    return {}


if __name__ == "__main__":
    with app.app_context():
        app.run(debug=True)
