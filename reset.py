from gym import db, create_app
from gym.models import Search, Gym, Info, Location, User, Post
from gym.config import Config

app = create_app(Config)
with app.app_context():
<<<<<<< HEAD

    #db reset 
    db.drop_all()
    db.create_all()
=======
    #example query
    Search.query.all()
    #db reset 
    db.drop_all()
    db.create_all()
>>>>>>> 46bc21424d6f2c37a9307383ed10a6158e4bb2b5
