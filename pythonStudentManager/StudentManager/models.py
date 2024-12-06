from cloudinary.provisioning import users
from  sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey
from StudentManager import app,db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(50), nullable=False)
    active = Column(Boolean, default=True)
    avatar = Column(String(200), default="https://res.cloudinary.com/dy1unykph/image/upload/v1729842193/iPhone_15_Pro_Natural_1_ltf9vr.webp")

    def __str__(self):
        self.name


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        import hashlib

        password = str(hashlib.md5("123".encode('utf-8')).hexdigest())

        u = User(name="Thịnh Thái", username="user", password=password)
        db.session.add(u)
        db.session.commit()  # Đừng quên commit để lưu thay đổi vào cơ sở dữ liệu

