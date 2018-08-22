from datetime import datetime
from gym import db, login_manager
from flask import current_app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s=Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        try:
            user_id=s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

#table used to define the many to many relationship bewteen Search and Gym
#with one search, we get many gyms and with one gym we can have many searches
search_gym = db.Table('search_gym', 
    db.Column('search_id', db.Integer, db.ForeignKey('search.id'), primary_key=True),
    db.Column('gym_id', db.Integer, db.ForeignKey('gym.id'), primary_key=True)
    )

class Search(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_input= db.Column(db.String(100), nullable=False)
    gyms = db.relationship("Gym", secondary=search_gym, lazy='subquery',
        backref=db.backref('searches', lazy=True))
    def __repr__(self):
        return "Search({})".format(self.user_input)

class Gym(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    search_id = db.Column(db.Integer, db.ForeignKey('search.id'))
    link = db.Column(db.String(150))
    logo_image_file = db.Column(db.String(40),default='default.jpg')
    name = db.Column(db.String(60))
    description=db.Column(db.String(60))
    locations = db.relationship('Location', backref='gym', lazy=True)

    def __repr__(self):
       return "Gym({})".format(self.name)

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gym_id = db.Column(db.Integer, db.ForeignKey('gym.id'))
    #place id is a string used by Google place details api to look for more detailsyyy
    place_id = db.Column(db.String(60))
    #this will link to google maps
    link = db.Column(db.String(150))
    address = db.Column(db.String(60))
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)

    def __repr__(self):
        return "Location({} location at {})".format(self.gym.name, self.address)