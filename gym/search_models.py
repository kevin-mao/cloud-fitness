from gym import db
from flask import current_app

class Search(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_input= db.Column(db.String(100), nullable=False)
    items = db.relationship('Items', backref='search', lazy=True)

    def __repr__(self):
        return str(self.id) + ": " + str(self.user_input)

# class List(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     search_id = db.Column(db.Integer, db.ForeignKey('search.id'))
#     search = db.relationship("Search", back_populates="list")
#     #search_user_input = db.Column(db.String(100), db.ForeignKey('search.user_input') )
#     items = db.relationship('Items', backref='list', lazy=True)
#
#     def __repr__(self):
#         return str(self.id) + ': ' + str(self.items)

class Items(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    search_id = db.Column(db.Integer, db.ForeignKey('search.id'))
    link = db.Column(db.String(150), unique=True, nullable=False, primary_key=True)
    logo_image_file = db.Column(db.String(40), nullable=False, default='default.jpg')
    gym_name = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return str(self.gym_name)