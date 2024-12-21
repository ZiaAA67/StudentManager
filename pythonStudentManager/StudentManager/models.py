from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime, Date, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from StudentManager import app, db
from flask_login import UserMixin
from enum import Enum as enum
import hashlib


class UserRole(enum):
    STAFF = 1
    ADMIN = 2
    TEACHER = 3
    STUDENT = 4


class Grade(enum):
    GRADE_10 = 1
    GRADE_11 = 2
    GRADE_12 = 3


class Base(db.Model):
    __abstract__ = True
    active = Column(Boolean, default=True)
    create_date = Column(DateTime, default=datetime.utcnow)
    update_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class User(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(20), nullable=False)
    # True = male ; False = female
    gender = Column(Boolean, nullable=False)
    address = Column(String(100), nullable=False)
    birth = Column(Date, nullable=False)
    phone = Column(String(12), nullable=False, unique=True)
    email = Column(String(50), nullable=False, unique=True)
    avatar = Column(String(255),
                    default="https://media.istockphoto.com/id/1337144146/vector/default-avatar-profile-icon-vector.jpg?s=612x612&w=0&k=20&c=BIbFwuv7FxTWvh5S3vB6bkT0Qv8Vn8N5Ffseq84ClGI=")
    role = Column(Enum(UserRole), default=UserRole.STAFF)

    def __str__(self):
        return self.full_name


class Account(Base, UserMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)

    user = relationship("User", backref="account")

    def __str__(self):
        return self.username


class Administrator(Base):
    id = Column(Integer, ForeignKey(User.id), primary_key=True)


class Teacher(Base):
    id = Column(Integer, ForeignKey(User.id), primary_key=True)
    degree = Column(String(50))
    subject = Column(String(50))


class Student(Base):
    id = Column(Integer, ForeignKey(User.id), primary_key=True)
    grade = Column(Enum(Grade), default=Grade.GRADE_10)
    gpa = Column(Float, default=0)


if __name__ == "__main__":
    with app.app_context():
        # tao bang
        db.create_all()

        teacher = User(full_name="TEACHER USER",
                       gender=True,
                       address="hcm city",
                       birth=datetime(2004, 1, 2),
                       phone="023675348",
                       email="nguyen@ou.com",
                       role=UserRole.TEACHER)
        db.session.add(teacher)
        db.session.commit()

        teacher_detail = Teacher(id=teacher.id, degree="Khong co", subject="Toan hoc")
        db.session.add(teacher_detail)
        db.session.commit()

        username = "teacher"
        password = str(hashlib.md5("123".encode('utf-8')).hexdigest())
        account = Account(username=username,
                          password=password,
                          user_id=teacher.id)
        db.session.add(account)
        db.session.commit()
