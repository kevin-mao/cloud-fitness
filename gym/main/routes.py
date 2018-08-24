from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from gym import db
from gym.models import Search, Gym, Location, Post
from gym.search.forms import SearchForm
from gym.search.scraper import scrape
from gym.search.maps_scraper import maps_scrape, get_place_details

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
        query = form.search.data.lower()
        return redirect(url_for('main.results', query=query))
    return render_template('home.html', title='Search', form=form, posts=posts)

@main.route("/about")
def about():
    return render_template('about.html', title='About')

@main.route("/blog")
def blog():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('blog.html', title='Blog', posts=posts)


@main.route("/results/query-<query>", methods=['GET'])
def results(query):
    form = SearchForm()
    check_searches = Search.query.filter_by(user_input=query).first()
    if check_searches ==None:
        search = Search(user_input=query)
        db.session.add(search)
        db.session.flush()
        info=maps_scrape(query)

        if info != 'ZERO_RESULTS':
            for result in info['results']:
                place_id = result['place_id']
                #it does have a google maps link tho (specific to each location)
                maps_link = get_place_details(place_id)['result']['url']
                name = result['name']
                address = result['formatted_address']
                lat = result['geometry']['location']['lat']
                lng = result['geometry']['location']['lng']
                #this photo reference can be used in the google places photo api
                # to get a posted picture, but it is not their logo
                #image = result['photo_reference']

                #get link and description with web scraping 
                link_and_description = scrape(query, name)
                link = link_and_description[0]
                description = link_and_description[1]  

                #check to see if this is just another location for a gym or a new gym
                check_gyms = Gym.query.filter_by(name=name).first()
                #if this is a new gym, create the Gym, a Location, and append
                if check_gyms == None:
                    gym = Gym(link=link, name=name, search_id=search.id, description=description)
                    location = Location(place_id=place_id, search_id=search.id, address=address, link=maps_link,lat=lat, lng=lng)
                    gym.locations.append(location)
                    search.gyms.append(gym)
                #if not, gym exists to create and append location
                else:
                    check_gyms.link = link
                    check_gyms.description = description
                    location = Location(place_id=place_id, address=address, search_id=search.id, link=maps_link, lat=lat, lng=lng)
                    check_gyms.locations.append(location)
                    search.gyms.append(check_gyms)

            #adds the search_object, then their gym, then their locations
            db.session.add(search)
            db.session.commit()
    else:
        search = check_searches
        #even though the search has been done before, we still need to update info 
        for gym in search.gyms:
            #get name and scrape 
            name = gym.name
            link_and_description = scrape(query, name)
            link = link_and_description[0]
            description = link_and_description[1]  

            #update 
            gym.link = link
            gym.description = description
            db.session.commit()

    gyms = search.gyms
    if len(gyms) == 0:
        flash('Did not find any gyms by {}'.format(search, search.user_input), 'danger')
    elif len(gyms) == 1:
        flash('Found {} gym by {}'.format(len(gyms),search.user_input), 'success')
    else:
        flash('Found {} gyms by {}'.format(len(gyms),search.user_input), 'success')
    return render_template('results.html', title="Search Results", form=form, search=search)


