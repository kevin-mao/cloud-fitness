from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from gym import db
from gym.models import Search, Gym, Info, Location, Post
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

#those weird where the franchise has a different name for each location
def check_name(name):
    parts = name.split(" ")
    if 'Crunch' in parts or 'Equinox' in parts: 
        name = parts[0]
    if name == 'LA FITNESS':
        name = 'LA Fitness'
    return name 

@main.route("/results/query-<query>", methods=['GET'])
def results(query):
    form = SearchForm()
    check_searches = Search.query.filter_by(user_input=query).first()

    #if this is a new search 
    if check_searches ==None:
        search = Search(user_input=query)
        db.session.add(search)
        db.session.commit()
        info=maps_scrape(query)

        if info != 'ZERO_RESULTS':
            #for each gym that is found 
            for result in info['results']:
                place_id = result['place_id']
                maps_link = get_place_details(place_id)['result']['url']
                gym_name = result['name']
                address = result['formatted_address']
                lat = result['geometry']['location']['lat']
                lng = result['geometry']['location']['lng']
                #this photo reference can be used in the google places photo api
                # to get a posted picture, but it is not their logo
                #image = result['photo_reference']

                #get link and description with web scraping 
                link_and_description = scrape(query, gym_name)
                link = link_and_description[0]
                description = link_and_description[1]  

                #check to see if this is just another location for a gym or a new gym
                gym_name = check_name(gym_name)
                check_gyms = Gym.query.filter_by(name=gym_name).first()
                #if this is a new gym, create the Gym, a Location, and append
                if check_gyms == None:
                    gym = Gym(name=gym_name, search_id=search.id)
                    location = Location(place_id=place_id, address=address, search_id=search.id, 
                        link=maps_link,lat=lat, lng=lng)
                    info = Info(link=link, description=description, search_id=search.id, gym_id=gym.id)
                #if not, gym exists, then check if location exists
                else:
                    gym = check_gyms
                    check_locations = Location.query.filter_by(address=address).first()
                    #if new location, create location 
                    if check_locations == None:
                        location = Location(place_id=place_id, address=address, 
                            search_id=search.id, link=maps_link, lat=lat, lng=lng)
                    #if location exists update its search id, so we know it corresponds to this search. 
                    else:
                        location = check_locations
                        location.search_id = search.id

                    #check gym info 
                    for i in gym.info: 
                        if i.search_id == search.id: 
                            if i.description != description and i.link != link:
                                info = Info(link=link, description=description, search_id=search.id, gym_id=gym.id)
                                #only append info if the gym does not have this link and description 
                                gym.info.append(info)
                gym.locations.append(location)
                search.gyms.append(gym)

            #store everything in db
            db.session.add(search)
            db.session.commit()
    else:
        search = check_searches
        #even though the search has been done before, we still need to update info 
        for gym in search.gyms:
            #get name and scrape 
            # gym_name = gym.name
            # link_and_description = scrape(query, gym_name)
            # link = link_and_description[0]
            # description = link_and_description[1]  

            #update 
            gym.search_id = search.id 
            # gym.link = link
            # gym.description = description
            db.session.commit()

    gyms = search.gyms
    if len(gyms) == 0:
        flash('Did not find any gyms by {}'.format(search, search.user_input), 'danger')
    elif len(gyms) == 1:
        flash('Found {} gym by {}'.format(len(gyms),search.user_input), 'success')
    else:
        flash('Found {} gyms by {}'.format(len(gyms),search.user_input), 'success')
    return render_template('results.html', title="Search Results", form=form, search=search)


