from flask_login import UserMixin
from __init__ import db


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    surname = db.Column(db.String(1000), nullable=False)
    name = db.Column(db.String(1000), nullable=False)
    patronymic = db.Column(db.String(1000), nullable=False)
    department = db.Column(db.String(1000), nullable=False)
    experience = db.Column(db.String(1000), nullable=False)
    salary = db.Column(db.Integer, nullable=False)
    login = db.Column(db.String(1000), unique=True, nullable=False)
    password = db.Column(db.String(1000), nullable=False)
    photo = db.Column(db.String(1000000), nullable=True)


class Jobs(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    text = db.Column(db.String(1000), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(Users.id), nullable=False)


class Quests(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(1000), nullable=False)
    description = db.Column(db.String(1000), nullable=False)


class Quest_parts(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(1000), nullable=False)
    text = db.Column(db.String(1000), nullable=False)
    quest_id = db.Column(db.Integer, db.ForeignKey(Quests.id), nullable=False)


class Walkthrough(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(Users.id), nullable=False)
    quest_id = db.Column(db.Integer, db.ForeignKey(Quests.id), nullable=False)
