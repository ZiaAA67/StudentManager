from flask_admin import  Admin
from flask_admin.contrib.sqla import ModelView
from sqlalchemy.testing.suite.test_reflection import users

from StudentManager import app,db


admin= Admin (app=app,name="Student Management Websie", template_mode="bootstrap4")

