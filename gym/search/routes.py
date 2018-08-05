from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from gym import db
from gym.models import Search
#need to create Search in models.py
from gym.search.forms import SearchForm

search = Blueprint('search', __name__)
app.register_blueprint(search)


@search.route("/search", methods=['GET', 'POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        #Search = Search(title=form.title.data, content=form.content.data, author=current_user)
        #needs to be changed to check if search has been made in database, if not then run search function
        #db.session.add(post)
        #db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('search.results'))
    return render_template('search.html', title='Search',
                           form=form)


@search.route("/results")
def results():
    #Returns a page with a list of gym with free passes for the area searched.
    # page = request.args.get('page', 1, type=int)
    # posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('post.html', title=, post=post)


