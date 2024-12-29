from models import *
import hashlib
from sqlalchemy import func, case


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
    classes = query.all()

    class_data = []
    for cls in classes:
        student_count = cls.students.filter(Student.active == True).count()
        class_data.append({
            "class": cls,
            "student_count": student_count
        })

    return class_data


def get_class_by_grade(grade):
    return Class.query.filter(Class.grade.__eq__(grade), Class.active == True).first()


def get_classes_by_grade(grade):
    return Class.query.filter(Class.grade.__eq__(grade), Class.active == True).all()


def get_class_by_id(class_id):
    return Class.query.get(class_id)


def count_students_in_class(class_id):
    cls = Class.query.filter(Class.id == class_id, Class.active == True).first()

    if cls:
        return len(cls.students)
    return 0


def get_students_by_class(class_id):
    students = Student.query.filter(Student.active == True, Student.class_id == class_id).all()
    return [
        {
            "id": student.id,
            "full_name": student.user_information.full_name,
            "grade": student.grade.value,
            "address": student.user_information.address,
            "birth": student.user_information.birth.strftime('%d-%m-%Y'),
            "phone": student.user_information.phone,
            "email": student.user_information.email
        }
        for student in students
    ]


def get_all_students(page=None):
    page_size = app.config.get("PAGE_SIZE")
    return Student.query.filter_by(active=True).paginate(page=page, per_page=page_size, error_out=False)


def check_phone_unique(phone):
    user_info = UserInformation.query.filter(UserInformation.phone.__eq__(phone),
                                             UserInformation.active == True).first()
    return user_info is None


def check_email_unique(email):
    user_info = UserInformation.query.filter(UserInformation.email.__eq__(email),
                                             UserInformation.active == True).first()
    return user_info is None


def init_school_rules():
    if not SchoolRules.query.first():
        new_rule = SchoolRules()
        db.session.add(new_rule)
        db.session.commit()


def count_subjects():
    return db.session.query(db.func.count(Subject.id)).filter(Subject.active == True).scalar()


def get_all_subjects(page=None):
    query = Subject.query
    if page:
        page_size = app.config["SUBJECTS_PAGE_SIZE"]
        start = (int(page) - 1) * page_size
        query = query.filter_by(active=True).slice(start, start + page_size)

    return query.all()


def get_subject_by_id(subject_id):
    return Subject.query.get(subject_id)


def get_subjects_by_grade(grade):
    return Subject.query.filter(Subject.grade.__eq__(grade),
                                Subject.active == True).all()


def get_years_semesters():
    years = db.session.query(Semester.year).group_by(Semester.year).all()
    return [year[0] for year in years]


def get_student_in_class():
    return db.session.query(Class.id, Class.name, func.count(Student.id)) \
        .join(Student, Student.class_id.__eq__(Class.id)).group_by(Class.id).all()


def get_class_statistics(year, semester, subject_id, grade=None):
    avg_scores = (
        db.session.query(
            Score.student_id,
            func.avg(Score.score).label("avg_score")
        )
        .join(TeachingPlan, Score.teaching_plan_id == TeachingPlan.id)
        .join(Semester, TeachingPlan.semester_id == Semester.id)
        .filter(
            Semester.year == year,
            Semester.semester == semester,
            TeachingPlan.subject_id == subject_id
        )
        .group_by(Score.student_id)
        .subquery()
    )

    query = (
        db.session.query(
            Class.id,
            Class.name.label("class_name"),
            func.count(Student.id).label("total_students"),
            func.sum(
                case(
                    (avg_scores.c.avg_score >= 5, 1),
                    else_=0
                )
            ).label("num_passed"),
            (
                    func.sum(
                        case(
                            (avg_scores.c.avg_score >= 5, 1),
                            else_=0
                        )
                    ) / func.count(Student.id) * 100
            ).label("pass_rate"),
        )
        .join(Student, Student.class_id == Class.id)
        .outerjoin(avg_scores, avg_scores.c.student_id == Student.id)
    )

    if grade:
        query = query.filter(Class.grade == grade)

    results = query.group_by(Class.id).all()

    print(f"Parameters -> Year: {year}, Semester: {semester}, Subject: {subject_id}, Grade: {grade}")

    return results


if __name__ == "__main__":
    with app.app_context():
        print(get_class_statistics("2024", 1, 1, Grade.GRADE_11))
