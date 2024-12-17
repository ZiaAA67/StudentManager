from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey
from StudentManager import app, db
from flask_login import UserMixin
import hashlib


class User(db.Model, UserMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    active = Column(Boolean, default=True)
    avatar = Column(String(255), default="https://media.istockphoto.com/id/1337144146/vector/default-avatar-profile-icon-vector.jpg?s=612x612&w=0&k=20&c=BIbFwuv7FxTWvh5S3vB6bkT0Qv8Vn8N5Ffseq84ClGI=")

    def __str__(self):
        self.name


if __name__ == "__main__":
    with app.app_context():
        # tao bang
        db.create_all()

        name = "ADMIN"
        username = "admin"
        password = str(hashlib.md5("123".encode('utf-8')).hexdigest())
        user = User(name=name, username=username, password=password)
        db.session.add(user)

        db.session.commit()

