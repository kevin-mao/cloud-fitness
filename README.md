# Work out for free! 

## Check DB
```
from gym import db, create_app
from gym.models import Search, Gym, Location, User, Post
from gym.config import Config

app = create_app(Config)
with app.app_context():
    #example query
    Search.query.all()

    #db reset 
    db.drop_all()
    db.create_all()
```
