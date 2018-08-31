from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from gym import db
from gym.models import Search, Gym, Location, Post, Info
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


# those weird where the franchise has a different name for each location
def check_name(name):
    parts = name.split(" ")
    if 'Crunch' in parts or 'Equinox' in parts:
        name = parts[0]
    if name == 'LA FITNESS':
        name = 'LA Fitness'
    return name


@main.route("/results/query-<query>", methods=['GET', 'POST'])
def results(query):
    form = SearchForm()

    if form.validate_on_submit():
        query = form.search.data.lower()
        return redirect(url_for('main.results', query=query))

    check_searches = Search.query.filter_by(user_input=query).first()

    # if this is a new search
    if check_searches == None:
        search = Search(user_input=query)
        db.session.add(search)
        db.session.flush()
        info = maps_scrape(query)

        if info != 'ZERO_RESULTS':
            # for each gym that is found
            for result in info['results']:
                place_id = result['place_id']
                maps_link = get_place_details(place_id)['result']['url']
                gym_name = result['name']
                address = result['formatted_address']
                lat = result['geometry']['location']['lat']
                lng = result['geometry']['location']['lng']
                # this photo reference can be used in the google places photo api
                # to get a posted picture, but it is not their logo
                # image = result['photo_reference']

                # check to see if this is just another location for a gym or a new gym
                gym_name = check_name(gym_name)
                print(gym_name)
                check_gyms = Gym.query.filter_by(name=gym_name, search_id=search.id).first()
                # if this is a new gym, create the Gym, a Location, and append
                if check_gyms == None:
                    gym = Gym(name=gym_name, search_id=search.id)
                    location = Location(place_id=place_id, address=address, search_id=search.id,
                                        link=maps_link, lat=lat, lng=lng)

                    db.session.add(gym)
                    db.session.flush()
                # if not, gym exists so just update it
                else:
                    gym = check_gyms
                    gym.search_id = search.id

                    check_locations = Location.query.filter_by(address=address).first()
                    # if new location, create location
                    if check_locations == None:
                        location = Location(place_id=place_id, address=address,
                                            search_id=search.id, link=maps_link, lat=lat, lng=lng)
                        # if location exists update its search id, so we know it corresponds to this search.
                    else:
                        location = check_locations
                        location.search_id = search.id
                    #update gym info 
                    gym.link = link
                    gym.description = description
                    gym.search_id = search.id

                gym.locations.append(location)
                search.gyms.append(gym)

                link_and_description = scrape(query, gym_name)
                link = link_and_description[0]
                description = link_and_description[1]

                # check gym info
                if gym.info == []:
                    info = Info(link=link, description=description, search_id=search.id, gym_id=gym.id)
                    gym.info.append(info)

                # else if it has info, if info is different add a new info
                else:
                    #links = [i.link for i in gym.info]
                    check_info = Info.query.with_parent(gym).filter_by(link=link).first()
                    # if info is new, create new Info object
                    # this should prevent duplicate info objects, but idk if it works
                    if check_info == None:
                        info = Info(link=link, description=description, search_id=search.id, gym_id=gym.id)
                        gym.info.append(info2)
                    # if info is right, just update search id
                    else:
                        info = check_info
                        info.search_id = search.id

            # store everything in db
            db.session.add(search)
            db.session.commit()
    else:
        search = check_searches
        # even though the search has been done before, we still need to update info
        for gym in search.gyms:
            # update
            gym.search_id = search.id
            db.session.add(gym)
            db.session.commit()

    gyms = search.gyms
    if len(gyms) == 0:
        flash('Did not find any gyms passes!', 'danger')
    elif len(gyms) == 1:
        flash('Found {} pass at this gyms by {}!'.format(len(gyms), query), 'success')
    else:
        flash('Found {} passes at these gyms by {}!'.format(len(gyms), query), 'success')
    return render_template('results.html', title="Search Results", form=form, search=search)