from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime, Enum, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from StudentManager import app, db
from flask_login import UserMixin
from enum import Enum as enum
import hashlib


class Role(enum):
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


class UserInformation(Base):
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
    role = Column(Enum(Role), default=Role.STAFF)

    def __str__(self):
        return self.full_name


class User(Base, UserMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    user_info_id = Column(Integer, ForeignKey(UserInformation.id), nullable=False)

    user_info = relationship("UserInformation", backref="user", uselist=False)

    def __str__(self):
        return self.username


class Administrator(Base):
    id = Column(Integer, ForeignKey(UserInformation.id), primary_key=True)


class Teacher(Base):
    id = Column(Integer, ForeignKey(UserInformation.id), primary_key=True)
    degree = Column(String(50))
    subject = Column(String(50))


class Student(Base):
    id = Column(Integer, ForeignKey(UserInformation.id), primary_key=True)
    grade = Column(Enum(Grade))
    gpa = Column(Float, default=0)


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
