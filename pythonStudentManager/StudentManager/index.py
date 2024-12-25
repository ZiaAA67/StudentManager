import re
from turtledemo.penrose import start

from flask_admin.model.typefmt import null_formatter

import dao
import cloudinary.uploader
from flask import render_template, request, redirect, session, jsonify, flash
from flask_login import login_user, current_user, logout_user
from datetime import datetime
from StudentManager import app, login
from models import *


# index
@app.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('index.html')
    return redirect('/login')


# student_admission
@app.route('/students', methods=['GET', 'POST'])
def student_management():
    grades = Grade.choices()
    page = request.args.get('page')
    students = dao.get_all_students(page=page)
    return render_template('employee/student_management.html', grades=grades, students=students)


# class_management
@app.route('/classes', methods=['get', 'post'])
def class_management():
    classes = dao.get_all_classes()

    return render_template("/employee/class_management.html", classes=classes)


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


# employee_profile
@app.route('/profile')
def employee_profile():
    user = dao.get_user_by_id(current_user.get_id())
    return render_template('/employee/employee_profile.html', username=user.username)


@app.context_processor
def common_attributes():
    if current_user.is_authenticated:
        return {
            "user_info": dao.get_user_info_by_user_id(user_id=current_user.get_id())
        }

    return {

    }


# lecturer
@app.route('/entry_score')
def entry_score():
    return render_template('/lecturer/entry_score.html')


@app.route('/export_score')
def export_score():
    return render_template('/lecturer/export_score.html')


@app.route('/api/classes', methods=['post'])
def add_class():
    class_name = request.json.get('class_name')
    grade_value = request.json.get('grade')

    # chuyển giá trị lấy được sang enum
    grade = Grade(int(grade_value))

    if Class.query.filter_by(name=class_name, grade=grade).first():
        return jsonify({"error": "Lớp đã tồn tại!"})

    new_class = Class(name=class_name, grade=grade)

    # Thêm vào database
    db.session.add(new_class)
    db.session.commit()

    return jsonify({"class": {
        "id": new_class.id,
        "name": new_class.name,
        "grade": new_class.grade.name
    }})


@app.route('/api/students/', methods=['POST'])
def add_student():
    try:
        # Tạo UserInformation
        gender = True if request.form.get('gender') == "Male" else False
        date_of_birth = request.form.get('date_of_birth')
        dob = datetime.strptime(date_of_birth, '%Y-%m-%d')

        phone = request.form.get('phone')
        if not is_valid_phone(phone):
            flash("Số điện thoại phải có 10 chữ số!", "error")
            return redirect('/students')

        if not is_valid_age(dob):
            flash("Độ tuổi phải từ 15 đến 20!", "error")
            return redirect('/students')

        user_info = UserInformation(
            full_name=request.form['name'],
            gender=gender,
            address=request.form['address'],
            birth=dob,
            phone=request.form['phone'],
            email=request.form['email'],
            role=Role.STUDENT
        )
        db.session.add(user_info)
        db.session.commit()

        grade_value = request.form.get('grade')
        grade = Grade(int(grade_value))
        student = Student(id=user_info.id, grade=grade)
        db.session.add(student)
        db.session.commit()

        flash("Thêm sinh viên thành công!", "success")
        return redirect('/students')


    except Exception as e:
        db.session.rollback()
        flash(f"Lỗi xảy ra: {str(e)}", "error")
        return redirect('/students')


def is_valid_phone(phone):
    return bool(re.match(r'^\d{10}$', phone))


def is_valid_age(birthdate):
    today = datetime.today()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    return 15 <= age <= 20


if __name__ == "__main__":
    with app.app_context():
        app.run(debug=True)
