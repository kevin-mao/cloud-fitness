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


class Search(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_input= db.Column(db.String(100), nullable=False)
    items = db.relationship('Items', backref='search', lazy=True)

    def __repr__(self):
        return "Search: " + str(self.user_input)

# class List(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     search_id = db.Column(db.Integer, db.ForeignKey('search.id'))
#     search = db.relationship("Search", back_populates="list")
#     #search_user_input = db.Column(db.String(100), db.ForeignKey('search.user_input') )
#     items = db.relationship('Items', backref='list', lazy=True)
#
#     def __repr__(self):
#         return str(self.id) + ': ' + str(self.items)

#gyms
class Items(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    search_id = db.Column(db.Integer, db.ForeignKey('search.id'))
    link = db.Column(db.String(150))
    logo_image_file = db.Column(db.String(40),default='default.jpg')
    gym_name = db.Column(db.String(60))
    gym_description=db.Column(db.String(60))

    def __repr__(self):
        return str('Item:' + self.gym_name)