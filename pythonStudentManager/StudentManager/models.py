from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime, Enum, Date, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from StudentManager import app, db
from flask_login import UserMixin
from enum import Enum as enum
import hashlib


# from StudentManager.dao import count_students_in_class, get_all_subjects


class Role(enum):
    STAFF = 1
    ADMIN = 2
    TEACHER = 3
    STUDENT = 4


class Grade(enum):
    GRADE_10 = 10
    GRADE_11 = 11
    GRADE_12 = 12

    @classmethod
    def choices(cls):
        return [(grade.value, str(grade)) for grade in cls]

    def __str__(self):
        return f"Khối {self.value}"


class ScoreType(enum):
    EXAM_15_MINS = 1
    EXAM_45_MINS = 2
    EXAM_FINAL = 3


class Base(db.Model):
    __abstract__ = True
    active = Column(Boolean, default=True)
    create_date = Column(DateTime, default=datetime.utcnow)
    update_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserInformation(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(50), nullable=False)
    # True = male ; False = female
    gender = Column(Boolean, nullable=False)
    address = Column(String(100), nullable=False)
    birth = Column(Date, nullable=False)
    phone = Column(String(10), nullable=False, unique=True)
    email = Column(String(50), nullable=False, unique=True)
    avatar = Column(String(255),
                    default="https://media.istockphoto.com/id/1337144146/vector/default-avatar-profile-icon-vector.jpg?s=612x612&w=0&k=20&c=BIbFwuv7FxTWvh5S3vB6bkT0Qv8Vn8N5Ffseq84ClGI=")
    role = Column(Enum(Role), default=Role.STAFF)

    def __str__(self):
        return self.full_name


class User(Base, UserMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    user_info_id = Column(Integer, ForeignKey(UserInformation.id), nullable=False)

    user_info = relationship('UserInformation', backref='user', uselist=False)

    def __str__(self):
        return self.username


class Administrator(Base):
    id = Column(Integer, ForeignKey(UserInformation.id), primary_key=True)


class Teacher(Base):
    id = Column(Integer, ForeignKey(UserInformation.id), primary_key=True)
    degree = Column(String(50))

    teaching_plans = relationship('TeachingPlan', backref='teacher')


class Class(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    grade = Column(Enum(Grade), nullable=False)

    students = relationship('Student', backref='class', lazy='dynamic')
    teaching_plan = relationship('TeachingPlan', backref='class', uselist=False)


class Student(Base):
    id = Column(Integer, ForeignKey(UserInformation.id), primary_key=True)
    class_id = Column(Integer, ForeignKey(Class.id), nullable=True)
    grade = Column(Enum(Grade), nullable=False)
    gpa = Column(Float, default=0)
    scores = relationship('Score', backref='student')

    user_information = relationship('UserInformation', backref='students', uselist=False)


class Subject(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    desc = Column(String(255))
    grade = Column(Enum(Grade), nullable=False)

    teaching_plans = relationship('TeachingPlan', backref='subject')
    exam_quantity = relationship("ExamQuantity", backref="subject", lazy=True)


class Semester(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    semester = Column(Integer, nullable=False)
    year = Column(String(4), nullable=False)
    teaching_plans = relationship('TeachingPlan', backref='semester', lazy=True)


class TeachingPlan(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    teacher_id = Column(Integer, ForeignKey(Teacher.id), nullable=False)
    subject_id = Column(Integer, ForeignKey(Subject.id), nullable=False)
    class_id = Column(Integer, ForeignKey(Class.id), nullable=False)
    semester_id = Column(Integer, ForeignKey(Semester.id), nullable=False)

    scores = relationship('Score', backref='teaching_plan', lazy=True)


class Score(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey(Student.id), nullable=False)
    teaching_plan_id = Column(Integer, ForeignKey(TeachingPlan.id), nullable=False)
    score_type = Column(Enum(ScoreType))
    score = Column(Float, default=0)


class ExamQuantity(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    subject_id = Column(Integer, ForeignKey(Subject.id), nullable=False)
    exam_type = Column(Enum(ScoreType), nullable=False)
    quantity = Column(Integer, default=1)


class SchoolRules(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    min_age = Column(Integer, default=15)
    max_age = Column(Integer, default=20)
    max_students_in_class = Column(Integer, default=40)


class Notification(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(50), nullable=False)
    content = Column(String(255), nullable=False)


if __name__ == "__main__":
    with app.app_context():
        # tao bang
        db.create_all()

        admin_user_info = UserInformation(full_name="ADMIN USER",
                                          gender=True,
                                          address="hcm city",
                                          birth=datetime(1999, 2, 12),
                                          phone="023675348",
                                          email="nguyen@ou.com",
                                          role=Role.ADMIN)
        db.session.add(admin_user_info)
        db.session.commit()
        admin_detail = Administrator(id=admin_user_info.id)
        db.session.add(admin_detail)
        db.session.commit()
        username = "admin"
        password = str(hashlib.md5("123".encode('utf-8')).hexdigest())
        account = User(username=username,
                       password=password,
                       user_info_id=admin_user_info.id)
        db.session.add(account)
        db.session.commit()

        teacher_user_info = UserInformation(full_name="Teacher User",
                                            gender=True,
                                            address="hcm city",
                                            birth=datetime(1999, 2, 12),
                                            phone="023675344",
                                            email="nguyenjss@ou.com",
                                            role=Role.TEACHER)
        db.session.add(teacher_user_info)
        db.session.commit()
        teacher_detail = Teacher(id=teacher_user_info.id, degree="Khong co")
        db.session.add(teacher_detail)
        db.session.commit()
        username = "teacher"
        password = str(hashlib.md5("123".encode('utf-8')).hexdigest())
        account = User(username=username,
                       password=password,
                       user_info_id=teacher_user_info.id)
        db.session.add(account)
        db.session.commit()

        employee_user_info = UserInformation(full_name="Employee User",
                                             gender=True,
                                             address="hcm city",
                                             birth=datetime(1999, 2, 12),
                                             phone="023675343",
                                             email="nguyenjsa@ou.com",
                                             role=Role.STAFF)
        db.session.add(employee_user_info)
        db.session.commit()
        username = "employee"
        password = str(hashlib.md5("123".encode('utf-8')).hexdigest())
        account = User(username=username,
                       password=password,
                       user_info_id=employee_user_info.id)
        db.session.add(account)
        db.session.commit()

        student_user_info = UserInformation(full_name="Student User",
                                            gender=True,
                                            address="hcm city",
                                            birth=datetime(1999, 2, 12),
                                            phone="023695343",
                                            email="nguynjsa@ou.com",
                                            role=Role.STUDENT)
        db.session.add(student_user_info)
        db.session.commit()
        student_detail = Student(id=student_user_info.id, grade=Grade.GRADE_10)
        db.session.add(student_detail)
        db.session.commit()

from random import choice, randint
from faker import Faker
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError

fake = Faker()


def generate_random_birth(min_age=15, max_age=20):
    today = datetime.today()
    start_date = today - timedelta(days=365 * max_age)
    end_date = today - timedelta(days=365 * min_age)
    return fake.date_between(start_date=start_date, end_date=end_date)


def generate_unique_phone():
    while True:
        phone = ''.join([str(randint(0, 9)) for _ in range(10)])
        if not UserInformation.query.filter_by(phone=phone).first():
            return phone


def generate_unique_email():
    while True:
        email = fake.unique.email()
        if not UserInformation.query.filter_by(email=email).first():
            return email


if __name__ == "__main__":
    with app.app_context():
        # Create teachers
        # teachers = []
        # for _ in range(6):
        #     full_name = fake.name()
        #     gender = choice([True, False])
        #     address = fake.address()
        #     birth = generate_random_birth(min_age=25, max_age=60)
        #     phone = generate_unique_phone()
        #     email = generate_unique_email()
        #     role = Role.TEACHER
        #     degree = choice(["Cử nhân", "Thạc sĩ", "Tiến sĩ"])
        #
        #     teacher_info = UserInformation(
        #         full_name=full_name,
        #         gender=gender,
        #         address=address,
        #         birth=birth,
        #         phone=phone,
        #         email=email,
        #         role=role
        #     )
        #     db.session.add(teacher_info)
        #     db.session.commit()
        #
        #     teacher_detail = Teacher(id=teacher_info.id, degree=degree)
        #     db.session.add(teacher_detail)
        #     db.session.commit()
        #
        #     teachers.append(teacher_detail)
        #
        # print(f"Successfully added {len(teachers)} teachers.")
        #
        # # Create classes
        # classes = []
        # class_names = ["10A", "10B", "11A", "11B", "12A", "12B"]
        # for class_name in class_names:
        #     grade_value = int(class_name[:2])
        #     grade = Grade(grade_value)
        #     new_class = Class(name=class_name, grade=grade)
        #     db.session.add(new_class)
        #     db.session.commit()
        #     classes.append(new_class)
        #
        # print(f"Successfully added {len(classes)} classes.")
        #
        # # Create students
        # students = []
        # student_index = 0
        # for class_obj in classes:
        #     for _ in range(40):
        #         if student_index >= 199:
        #             break
        #
        #         full_name = fake.name()
        #         gender = choice([True, False])
        #         address = fake.address()
        #         birth = generate_random_birth()
        #         phone = generate_unique_phone()
        #         email = generate_unique_email()
        #         role = Role.STUDENT
        #
        #         student_info = UserInformation(
        #             full_name=full_name,
        #             gender=gender,
        #             address=address,
        #             birth=birth,
        #             phone=phone,
        #             email=email,
        #             role=role
        #         )
        #         db.session.add(student_info)
        #         db.session.commit()
        #
        #         student_detail = Student(id=student_info.id, grade=class_obj.grade, class_id=class_obj.id)
        #         db.session.add(student_detail)
        #         db.session.commit()
        #
        #         students.append(student_detail)
        #         student_index += 1
        #
        # # Add remaining students without classes
        # for _ in range(30):
        #     full_name = fake.name()
        #     gender = choice([True, False])
        #     address = fake.address()
        #     birth = generate_random_birth()
        #     phone = generate_unique_phone()
        #     email = generate_unique_email()
        #     role = Role.STUDENT
        #     grade = choice(list(Grade))
        #
        #     student_info = UserInformation(
        #         full_name=full_name,
        #         gender=gender,
        #         address=address,
        #         birth=birth,
        #         phone=phone,
        #         email=email,
        #         role=role
        #     )
        #     db.session.add(student_info)
        #     db.session.commit()
        #
        #     student_detail = Student(id=student_info.id, grade=grade)
        #     db.session.add(student_detail)
        #     db.session.commit()
        #
        #     students.append(student_detail)
        #     student_index += 1
        #
        # print(f"Successfully added {len(students)} students.")
        #
        # # Create subjects for each grade
        # subjects = ["Toán", "Văn", "Anh"]
        # for grade in Grade:
        #     for subject_name in subjects:
        #         subject = Subject(name=subject_name, desc=f"Môn {subject_name} khôi {grade.value}", grade=grade)
        #         db.session.add(subject)
        # db.session.commit()
        #
        # print("Successfully added subjects for all grades.")

        # new_semester = Semester(semester=1, year="2024")
        # db.session.add(new_semester)
        # db.session.commit()

        # teacher = Teacher.query.first()
        # subject = Subject.query.first()
        # class_ = Class.query.first()
        # semester = Semester.query.first()
        #
        # new_teaching_plan = TeachingPlan(
        #     teacher_id=teacher.id,
        #     subject_id=subject.id,
        #     class_id=class_.id,
        #     semester_id=semester.id,
        # )
        # db.session.add(new_teaching_plan)
        # db.session.commit()
        print("New teaching plan created successfully!")
