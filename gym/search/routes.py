from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from gym import db
from gym.models import Search, Items
from gym.search.forms import SearchForm
from gym.search.scraper import *

search = Blueprint('search', __name__)

@search.route("/search", methods=['GET', 'POST'])
def websearch():
    form = SearchForm()
    if form.validate_on_submit():
        query = Search(user_input=form.search.data)
        check_db = Search.query.filter_by(user_input=query.user_input).first()

        if check_db==None:
            info=scraper.main(query.user_input)
            item_count=0
            results=[]
            for result in info:
                link = result[0]
                name = result[1]
                image = result[2]
                item = Items(link=link, logo_image_file=image, gym_name=name, id=item_count, search=query)
                item_count += 1
                results.append(item)
            db.session.add(query)
            db.session.commit()
        else:
            results = check_db.items

        return redirect(url_for('results'), title='Search Results', results=results)
    return render_template('search.html', title='Search',
                           form=form)


@search.route("/results")
def results():
    #Returns a page with a list of gym with free passes for the area searched.
    return render_template('results.html', title='Search Results')


