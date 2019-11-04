from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from auth import Authenticator
from datetime import datetime

db = SQLAlchemy()
auth = Authenticator()


def init_app(app):
    app.config.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', False)
    db.init_app(app)
    auth.set_app(app)


# [START model]
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    admin = db.Column(db.Boolean, nullable=False)
    giftable = db.relationship('Giftable', lazy=False, uselist=False)
    redeemable = db.relationship('Redeemable', lazy=False, uselist=False)

    def __repr__(self):
        return "<User(id=%s, username='%s', admin=%s)>" % (self.id, self.username, self.admin)


class Giftable(db.Model):
    __tablename__ = 'giftables'

    userid = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    balance = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return "<Giftable(userid=%s, balance=%s)>" % (self.userid, self.balance)


class Redeemable(db.Model):
    __tablename__ = 'redeemables'

    userid = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    balance = db.Column(db.BigInteger, nullable=False)

    def __repr__(self):
        return "<Redeemable(userid=%s, balance=%s)>" % (self.userid, self.balance)


class Gift(db.Model):
    __tablename__ = 'gifts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    giverid = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiverid = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.DateTime(timezone=True), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    message = db.Column(db.String(255))

    def __repr__(self):
        return "<Gift(id=%s, message=%s, amount=%s)>" % (self.id, self.message, self.amount)


class Redemption(db.Model):
    __tablename__ = 'redemptions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userid = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.DateTime(timezone=True), nullable=False)
    cards = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return "<Redemption(id=%s, userid=%s, cards=%s)>" % (self.id, self.userid, self.cards)


class Month(db.Model):
    __tablename__ = 'month'

    id = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return "<Month(id=%s, month=%s)>" % (self.id, self.month)


# [END model]

def authenticate(username, password):
    user = User.query.filter(User.username == username).first()

    if user and auth.check_hash(user.password, password):
        return user


def create_user(data):
    if data['password'] != data['passwordDuplicate']:
        raise ValueError('Passwords do not match')
    data.pop('passwordDuplicate')

    if data['username'] is '' or data['password'] is '':
        raise ValueError('Invalid username or password')

    data.update({
        'password': auth.make_hash(data['password']),
        'admin': False
    })

    user = create(User, data)
    create(Giftable, {
        'userid': user.id,
        'balance': 1000
    })
    create(Redeemable, {
        'userid': user.id,
        'balance': 0
    })

    db.session.commit()


def details(user_id):
    user = one(User, user_id)
    usernames = [u.username for u in many(User)]
    usernames.remove(user.username)

    return user, usernames


def gift(giver_id, receiver_username, amount, message):
    receiver = User.query.filter(User.username == receiver_username).first()

    if amount > receiver.giftable.balance:
        raise ValueError('The user cannot gift that amount.')

    db.session.execute(f'''CALL giftpoints({giver_id}, {receiver.id}, {amount}, '{message}');''')
    db.session.commit()


def redeem(user_id, cards):
    points = cards * 10000
    redeemable = one(Redeemable, user_id)

    print(points)

    if points > redeemable.balance:
        raise ValueError('The user cannot redeem that amount.')

    print(points)

    setattr(redeemable, 'balance', redeemable.balance - points)
    create(Redemption, {
        'userid': user_id,
        'date': datetime.now(),
        'cards': cards
    })

    db.session.commit()


# [START crud]
def create(model, data):
    row = model(**data)
    db.session.add(row)
    db.session.flush()
    return row


def one(model: db.Model, key):
    return model.query.get(key)


def many(model: db.Model):
    return model.query.all()


def delete(model, key):
    model.query.filter_by(id=key).delete()
    db.session.flush()


# [END crud]

# _____


def _create_database():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    init_app(app)
    with app.app_context():
        db.create_all()
        db.session.execute('''DROP PROCEDURE IF EXISTS giftpoints;''')
        db.session.execute('''
        CREATE PROCEDURE giftpoints(
            IN giverid INTEGER, 
            IN receiverid INTEGER, 
            IN amount INTEGER, 
            IN message VARCHAR(255)
        ) 
        BEGIN
        
        # deduct point from giftable
        UPDATE giftables set balance=(balance-amount) WHERE userid = giverid;
    
        # increase point for redeemable
        UPDATE redeemables set balance=(balance+amount) WHERE userid = receiverid;
    
        # create an entry in gifts table
        INSERT INTO gifts (giverid, receiverid, date, amount, message) 
        VALUES (giverid, receiverid, NOW(), amount, message);
        END;
        ''')
        db.session.commit()

    print("All tables created")


if __name__ == '__main__':
    _create_database()
