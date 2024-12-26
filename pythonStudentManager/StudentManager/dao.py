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


def count_classes():
    return db.session.query(db.func.count(Class.id)).filter(Class.active == True).scalar()


def get_all_classes(page=None):
    query = Class.query
    if page:
        page_size = app.config["CLASSES_PAGE_SIZE"]
        start = (int(page) - 1) * page_size
        query = query.filter_by(active=True).slice(start, start + page_size)

    return query.all()


def get_all_students(page=None):
    page_size = app.config.get('STUDENTS_PAGE_SIZE')
    return Student.query.paginate(page=page, per_page=page_size, error_out=False)


def init_school_rules():
    if not SchoolRules.query.first():
        new_rule = SchoolRules()
        db.session.add(new_rule)
        db.session.commit()


if __name__ == "__main__":
    print()
