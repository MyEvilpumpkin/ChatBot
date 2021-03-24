from flask_login import UserMixin
from __init__ import db


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    surname = db.Column(db.String(1000))
    name = db.Column(db.String(1000))
    patronymic = db.Column(db.String(1000))
    department = db.Column(db.String(1000))
    experience = db.Column(db.String(1000))
    salary = db.Column(db.Integer)
    login = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    photo = db.Column(db.String(1000000))
