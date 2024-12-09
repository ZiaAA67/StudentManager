from operator import index

import cloudinary.uploader
from flask import render_template, request, redirect
from flask_login import login_user, current_user, logout_user
from sqlalchemy.testing.provision import register

import dao
from StudentManager import app, login




# index
@app.route('/')
def index():
    return render_template("index.html")


#homepage
@app.route("/home_page")
def home_page():
    return render_template('home_page.html')


#student_admission
@app.route('/student_admission')
def student_admission():
    return render_template("student_management.html")

#class_management
@app.route('/class_management')
def class_management():
    return render_template("class_management.html")

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
        return render_template("home_page.html")
    err_msg = None
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        user = dao.auth_user(username=username, password=password)
        if user:
            login_user(user)
            return render_template('home_page.html')
        else:
            err_msg = "Tài khoản hoặc mật khẩu không đúng!"

    return render_template('index.html', err_msg=err_msg)

@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id=user_id)

#logout
@app.route('/logout')
def logout_my_user():
    logout_user()
    return redirect('/login')

#profile
@app.route('/profile')
def profile():
    return render_template("profile.html")


if __name__ == "__main__":
    with app.app_context():
        app.run(debug=True)
