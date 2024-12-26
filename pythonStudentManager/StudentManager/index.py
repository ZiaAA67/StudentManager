import re
from email.policy import default
from mmap import PAGESIZE
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
@app.route('/students', methods=['get', 'post'])
def student_management():
    page = request.args.get('page', 1, type=int)
    students_paginated = dao.get_all_students(page)
    grades = Grade.choices()

    return render_template('employee/student_management.html',
                           students=students_paginated.items,
                           grades=grades,
                           pagination=students_paginated)


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


@app.route('/api/students/', methods=['post'])
def add_student():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data"}), 400

    name = data.get('name')
    gender = True if data.get('gender') == "Male" else False
    date_of_birth = data.get('date_of_birth')
    dob = datetime.strptime(date_of_birth, '%Y-%m-%d')
    address = data.get('address')
    phone = data.get('phone')
    email = data.get('email')
    grade_value = data.get('grade')
    grade = Grade(int(grade_value))

    if not name or not date_of_birth or not address or not phone or not email or not grade_value:
        return jsonify({"error": "Lack of information"}), 400

    if not is_valid_phone(phone):
        return jsonify({"error": "Number phone must be 10 numbers"}), 400

    if not is_valid_age(dob):
        return jsonify({"error": "Age between 15 - 20"}), 400

    new_user_info = UserInformation(full_name=name, gender=gender, address=address, birth=dob, phone=phone,
                                    email=email, role=Role.STUDENT);

    db.session.add(new_user_info)
    db.session.commit()

    new_student = Student(id=new_user_info.id, grade=grade)
    db.session.add(new_student)
    db.session.commit()

    return jsonify({"student": {"name": name, "gender": gender, "date_of_birth": dob.strftime('%Y-%m-%d')}})


def is_valid_phone(phone):
    return bool(re.match(r'^\d{10}$', phone))


def is_valid_age(birthdate):
    today = datetime.today()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    return 15 <= age <= 20


if __name__ == "__main__":
    with app.app_context():
        app.run(debug=True)
