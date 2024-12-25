from models import *
import hashlib


def auth_user(username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    return User.query.filter(User.username.__eq__(username.strip()),
                             User.password.__eq__(password)).first()


def add_user(name, username, password, avatar):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    u = User(name=name, username=username, password=password, avatar=avatar)
    db.session.add(u)
    db.session.commit()


def get_user_by_id(user_id):
    return User.query.get(user_id)


def get_user_info_by_id(user_info_id):
    return UserInformation.query.get(user_info_id)


def get_user_info_by_user_id(user_id):
    user = get_user_by_id(user_id)
    return UserInformation.query.get(user.user_info_id)


def get_all_classes():
    return Class.query.all()


def get_all_students(page=None):
    if page:
        page_size = app.config['PAGE_SIZE']
        start = (int(page) - 1) * page_size
        return Student.query.slice(start, start + page_size)
    return Student.query.all()


def add_user_info(full_name, gender, address, birth, phone, email, avatar, role):
    full_name = str(full_name.strip())
    email = email.strip()
    user_information = UserInformation(full_name=full_name, gender=gender, address=address, birth=birth,
                                       phone=phone, email=email, avatar=avatar, role=role)
    db.session.add(user_information)
    db.session.commit()


def add_student(id, grade):
    student = Student(id=id, grade=grade)


if __name__ == "__main__":
    print()
