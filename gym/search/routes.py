from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from gym import db
from gym.models import Search, Items
from gym.search.forms import SearchForm
from gym.search.scraper import main

search = Blueprint('search', __name__)


@search.route("/search", methods=['GET', 'POST'])
def websearch():
    form = SearchForm()
    if form.validate_on_submit():
        query = Search(user_input=form.search.data)
        check_db = Search.query.filter_by(user_input=query.user_input).first()

        if check_db==None:
            info=main(query.user_input)
            results=[]
            for result in info:
                link = result[0]
                name = result[1]
                image = result[2]
                item = Items(link=link, logo_image_file=image, gym_name=name, search=query)
                results.append(item)
            db.session.add(query)
            db.session.commit()
        else:
            results = check_db.items

        return render_template('results.html', title='Search Results', results=results)
    return render_template('home.html', title='Search',
                           form=form)


@search.route("/results",methods=['GET', 'POST'])
def results():
    #Returns a page with a list of gym with free passes for the area searched.
    return render_template('results.html', title='Search Results', results=results)


