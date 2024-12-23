import dao
import cloudinary.uploader
from flask import render_template, request, redirect
from flask_login import login_user, current_user, logout_user
from StudentManager import app, login
from models import *


# index
@app.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('index.html')
    return redirect('/login')


# # homepage
# @app.route("/employee/home_page_employee")
# def home_page():
#     return render_template('/employee/home_page_employee.html')


# student_admission
@app.route('/students')
def student_admission():
    return render_template("/employee/student_management.html")


# class_management
@app.route('/classes', methods=["get", "post"])
def class_management():
    if request.method.__eq__('POST'):
        class_name = request.form.get('class_name')
        grade_value = request.form.get('grade')
        grade = Grade(int(grade_value))

        print(class_name, grade)

    return render_template("/employee/class_management.html")


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
#lecturer
@app.route('/entry_score')
def entry_score():
    return render_template('/lecturer/entry_score.html')

@app.route('/export_score')
def export_score():
    return render_template('/lecturer/export_score.html')


if __name__ == "__main__":
    with app.app_context():
        app.run(debug=True)
