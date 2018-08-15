# Work out for free! 

## Check DB
```
from gym import db, create_app
from gym.models import Search, Items, User, Posts
from gym.config import Config

app= create_app(Config)
with app.app_context():
    #exmple query
    Search.query.all()
```
