import datetime

from flask.ext.bcrypt import generate_password_hash
from flask.ext.login import UserMixin
from peewee import *

DATABASE = SqliteDatabase('taco_cat.db')

class User(UserMixin, Model):
    email = CharField(unique=True)
    password = CharField(max_length=100)
    joined_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = DATABASE
        order_by = ('-joined_at',)

    @classmethod
    def create_user(cls, email, password):
        try:
            cls.create(
                email=email,
                password=generate_password_hash(password)
            )
        except IntegrityError:
            raise ValueError('Email unavailable.')


class Taco(Model):
    timestamp = DateTimeField(default=datetime.datetime.now)
    user = ForeignKeyField(model=User, backref='tacos')
    protein = CharField()
    shell = CharField()
    cheese = BooleanField(default=False)
    extras = TextField()

    class Meta:
        database = DATABASE
        order_by = ('-timestamp',)


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, Taco], safe=True)
    DATABASE.close()
