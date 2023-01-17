from . import database
from flask_login import UserMixin
from sqlalchemy.sql import func, expression


class User(database.Model, UserMixin):
    __tablename__ = 'users'
    id = database.Column(database.Integer, primary_key=True)
    first_name = database.Column(database.String(64), nullable=False)
    last_name = database.Column(database.String(64), nullable=False)
    email = database.Column(database.String(128), unique=True, nullable=False)
    password = database.Column(database.String(128), nullable=False)
    balance = database.Column(database.Integer, nullable=False, server_default='0')
    created_at = database.Column(database.DateTime, server_default=func.now())
    modified_at = database.Column(database.DateTime, server_default=func.now(), server_onupdate=func.now())

    def __init__(self, first_name, last_name, email, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password


class Item(database.Model):
    __tablename__ = 'items'
    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(128), nullable=False)
    price = database.Column(database.Integer, nullable=False)
    on_sale = database.Column(database.Boolean, nullable=False, server_default=expression.true())
    description = database.Column(database.Text)
    owner = database.Column(database.Integer, database.ForeignKey('users.id'), nullable=False)
    hw_id = database.Column(database.String(32))

    def __init__(self, name, price, description, owner, hw_id):
        self.name = name
        self.price = price
        self.description = description
        self.owner = owner
        self.hw_id = hw_id


class Transaction(database.Model):
    __tablename__ = 'transactions'
    id = database.Column(database.Integer, primary_key=True)
    date = database.Column(database.DateTime, server_default=func.now())
    amount = database.Column(database.Integer, nullable=False)
    from_user = database.Column(database.Integer, database.ForeignKey('users.id'), nullable=False)
    to_user = database.Column(database.Integer, database.ForeignKey('users.id'), nullable=False)
    item = database.Column(database.Integer, database.ForeignKey('items.id'), nullable=False)

    def __init__(self, amount, from_user, to_user, item):
        self.amount = amount
        self.from_user = from_user
        self.to_user = to_user
        self.item = item


class Coupon(database.Model):
    __tablename__ = 'coupons'
    code = database.Column(database.String(32), primary_key=True)
    amount = database.Column(database.Integer, nullable=False)
    used = database.Column(database.Boolean, nullable=False, server_default=expression.false())
    used_by = database.Column(database.Integer, database.ForeignKey('users.id'))

    def __int__(self, code, amount, used, used_by):
        self.code = code
        self.amount = amount
        self.used = used
        self.used_by = used_by
