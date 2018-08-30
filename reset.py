from gym import db, create_app
from gym.models import Search, Gym, Info, Location, User, Post
from gym.config import Config

app = create_app(Config)
with app.app_context():
    #db reset 
    db.drop_all()
    db.create_all()
