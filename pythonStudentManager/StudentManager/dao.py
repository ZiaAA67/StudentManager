from datetime import date

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
    school_rule = init_school_rules()
    max_students = school_rule.max_students_in_class

    classes = Class.query.filter(
        Class.grade == grade,
        Class.active == True
    ).all()

    for cls in classes:
        if cls.students.count() < max_students:
            return cls

    return None


def get_classes_by_grade(grade):
    return Class.query.filter(Class.grade.__eq__(grade), Class.active == True).all()


def get_class_by_id(class_id):
    return Class.query.get(class_id)


def count_students_in_class(class_id):
    cls = Class.query.filter(Class.id == class_id, Class.active == True).first()

    if cls:
        return cls.students.count()
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
    rule = SchoolRules.query.order_by(SchoolRules.create_date.desc()).first()
    if not rule:
        rule = SchoolRules()
        db.session.add(rule)
        db.session.commit()

    return rule


def count_subjects():
    return db.session.query(db.func.count(Subject.id)).filter(Subject.active == True).scalar()


def count_notifications():
    return db.session.query(db.func.count(Notification.id)).filter(Subject.active == True).scalar()


def get_all_subjects(page=None):
    query = Subject.query
    if page:
        page_size = app.config["SUBJECTS_PAGE_SIZE"]
        start = (int(page) - 1) * page_size
        query = query.filter_by(active=True).slice(start, start + page_size)

    return query.all()


def get_all_notifications(page=None):
    query = Notification.query.filter_by(active=True)

    if page:
        page_size = app.config["NOTIFICATIONS_PAGE_SIZE"]
        start = (int(page) - 1) * page_size
        query = query.order_by(Notification.create_date.desc()).slice(start, start + page_size)
    else:
        query = query.order_by(Notification.create_date.desc())

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


def calculate_average_score(scores):
    """
    - 15 phút: hệ số 1
    - 45 phút: hệ số 2
    - Thi cuối kỳ: hệ số 3
    """
    total_score = 0
    total_weight = 0

    for score in scores:
        if score.score_type == ScoreType.EXAM_15_MINS:
            weight = 1  # hệ số cho 15 phút
        elif score.score_type == ScoreType.EXAM_45_MINS:
            weight = 2  # hệ số cho 45 phút
        elif score.score_type == ScoreType.EXAM_FINAL:
            weight = 3  # hệ số cho thi cuối kỳ
        else:
            weight = 1  # mặc định nếu không thuộc loại trên

        total_score += score.score * weight
        total_weight += weight

    if total_weight == 0:
        return 0  # tránh chia cho 0 nếu không có điểm

    return total_score / total_weight


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


def get_lastest_exam_quantities(subject_id):
    default_quantities = {
        ScoreType.EXAM_15_MINS.name: 2,
        ScoreType.EXAM_45_MINS.name: 1,
        ScoreType.EXAM_FINAL.name: 1
    }

    for score_type in ScoreType:
        latest_record = ExamQuantity.query.filter(ExamQuantity.active == True,
                                                  ExamQuantity.subject_id == subject_id,
                                                  ExamQuantity.exam_type == score_type,
                                                  ).order_by(ExamQuantity.update_date.desc()).first()

        if latest_record:
            default_quantities[score_type.name] = latest_record.quantity

    return default_quantities


def get_teaching_plan(class_id, subject_id, semester_id, teacher_id):
    teaching = TeachingPlan.query.filter_by(class_id=class_id, subject_id=subject_id, semester_id=semester_id,
                                            teacher_id=teacher_id).first()
    if not teaching:
        teaching = TeachingPlan(class_id=class_id, subject_id=subject_id, semester_id=semester_id,
                                teacher_id=teacher_id)
        db.session.add(teaching)
        db.session.commit()
    return teaching


def save_score(student_id, teaching_plan_id, score_type, score_value, index):
    existing_score = Score.query.filter_by(
        student_id=student_id,
        teaching_plan_id=teaching_plan_id,
        score_type=score_type,
        index=index
    ).first()

    if existing_score:
        existing_score.score = score_value
    else:
        new_score = Score(
            student_id=student_id,
            teaching_plan_id=teaching_plan_id,
            score_type=score_type,
            index=index,
            score=score_value
        )
        db.session.add(new_score)

    db.session.commit()


def get_semester(semester_value):
    year = date.today().year
    semester = Semester.query.filter(Semester.active == True, Semester.semester == semester_value,
                                     Semester.year == year).first()
    if not semester:
        semester = Semester(semester=semester_value, year=year)
        db.session.add(semester)
        db.session.commit()
    return semester


def get_scores_by_subject_and_semester(student_ids, subject_id, semester_id, class_id, teacher_id):
    teaching_plan = get_teaching_plan(class_id=class_id, subject_id=subject_id, semester_id=semester_id,
                                      teacher_id=teacher_id)
    print(subject_id, semester_id, class_id)
    print(teaching_plan)

    scores = Score.query.filter(Score.student_id.in_(student_ids), Score.teaching_plan_id == teaching_plan.id) \
        .order_by(Score.create_date.desc()).all()

    return scores


if __name__ == "__main__":
    with app.app_context():
        print("Hello world!")
        print(get_class_statistics("2024", 1, 1, Grade.GRADE_10))
