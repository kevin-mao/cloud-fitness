from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from gym import db
from gym.models import Search, Items, Post
from gym.search.forms import SearchForm
from gym.search.scraper import scrape

main = Blueprint('main', __name__)


# @main.route("/")
# @main.route("/home")
# def home():
#     page = request.args.get('page', 1, type=int)
#     posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
#     return render_template('home.html', posts=posts)

@main.route("/", methods=['GET', 'POST'])
@main.route("/home", methods=['GET', 'POST'])
def home():
    form = SearchForm()
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)

    if form.validate_on_submit():
        search = form.search.data.lower()
        return redirect(url_for('main.results', search=search))
    return render_template('home.html', title='Search', form=form, posts=posts)

@main.route("/about")
def about():
    return render_template('about.html', title='About')

@main.route("/blog")
def blog():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('blog.html', title='Blog', posts=posts)


@main.route("/results/search-<search>", methods=['GET'])
def results(search):
    search_object = Search(user_input=search)
    check_db = Search.query.filter_by(user_input=search).first()

    if check_db==None:
        info=scrape(search)
        results=[]
        for result in info:
            link = result[0]
            name = result[1]
            image = result[2]
            item = Items(link=link, logo_image_file=image, gym_name=name, search=search_object)
            results.append(item)
        db.session.add(search_object)
        db.session.commit()
    else:
        results = check_db.items

    return render_template('results.html', title="Search Results", results=results)


