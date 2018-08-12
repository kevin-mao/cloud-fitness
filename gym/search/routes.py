from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from gym import db
from gym.models import Search
from gym.search.forms import SearchForm
from gym.search.scraper import *

search = Blueprint('search', __name__)

@search.route("/search", methods=['GET', 'POST'])
def websearch():
    form = SearchForm()
    if form.validate_on_submit():
        Search = Search(content=form.content.data)
        query = Search.query.filter_by(user_input=Search).first()
        if query==None:
            scraper.main()
            #run scraper function


        #else:
            #Use results from that prior query already stored

        return redirect(url_for('search.results'))
    return render_template('search.html', title='Search',
                           form=form)


@search.route("/results")
def results():
    #Returns a page with a list of gym with free passes for the area searched.
    # page = request.args.get('page', 1, type=int)
    # posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('post.html', title='Searh Results', post=post)


