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

## Work in branches

check which branch 
```
git branch 
```
switch branches
```
git checkout info_db
git checkout master
```
push/pull both branches (remember to add and commit)
```
git push origin master info_db
git pull origin master info_db
```
merging branches 
first check to make sure master is up to date 
```
git fetch 
git branch -va 

git merge info_db
```

