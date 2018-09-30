from _sqlite3 import OperationalError
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
import time
from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from gym import db
from gym.models import Search, Gym, Location, Post, Info
from gym.search.forms import SearchForm
from gym.search.scraper import scrape
from gym.search.maps_scraper import maps_scrape, get_place_details, abbreviation_fixer
from flask_login import login_required
import json
import csv

def get_key():
    with open('./gym/static/csv/key.csv', 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        for line in csv_reader:
            key=line[0]
        return key
API_KEY = get_key()

main = Blueprint('main', __name__)
locations_coordinates = {}

@main.route("/", methods=['GET', 'POST'])
@main.route("/home", methods=['GET', 'POST'])
def home():
    form = SearchForm()
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)

    if request.method == 'POST' and form.validate():
        query = form.search.data.lower()
        range = form.range.data
        return redirect(url_for('main.search', query=query))
    return render_template('home.html', form=form, posts=posts)

@main.route("/about")
def about():
    return render_template('about.html', title='About')

@main.route("/blog")
def blog():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('blog.html', title='Blog', posts=posts)

@main.route("/coordinates", methods=['GET', 'POST'])
def send_coordinates():
    #print(locations_coordinates)
    return json.dumps({"data": locations_coordinates})

@main.route("/search/<query>", methods=['GET', 'POST'])
def search(query):
    query=abbreviation_fixer(query)
    locations_coordinates.clear()

    check_searches = Search.query.filter_by(user_input=query).first()
    # if this is a new search
    if check_searches == None:
        #center lat,lng are the coordinates of the gym 
        center_lat, center_lng, info = maps_scrape(query)
        search = Search(user_input=query,lat=center_lat, lng=center_lng)
        while True:
            try:
                center_lat, center_lng, info = maps_scrape(query)
                search = Search(user_input=query, lat=center_lat, lng=center_lng)
                db.session.add(search)
                db.session.flush()
            except exc.OperationalError:
                time.sleep(10)
                db.session.rollback()
                print("exception")
            break
        if info != 0:
            # for each gym that is found
            for result in info['results']:
                place_id = result['place_id']
                lat = result['geometry']['location']['lat']
                lng = result['geometry']['location']['lng']

                maps_link, gym_name, address = get_place_details(place_id)
                # this photo reference can be used in the google places photo api
                # to get a posted picture, but it is not their logo
                # image = result['photo_reference']

                #add data to location coordinates api
                if locations_coordinates == {}:
                    locations_coordinates['center'] = [center_lat, center_lng]
                    locations_coordinates['gyms']=[{'name': gym_name, 'coordinates':[lat, lng], 'link': maps_link, 
                    'address': address}]
                else:
                    locations_coordinates['gyms'].append({'name': gym_name, 'coordinates':[lat, lng], 
                        'link': maps_link, 'address': address})

                check_gyms = Gym.query.filter_by(name=gym_name).first()
                # if this is a new gym, create the Gym, a Location, and append
                if check_gyms == None:
                    gym = Gym(name=gym_name, search_id=search.id)
                    location = Location(place_id=place_id, address=address, search_id=search.id,
                                        link=maps_link, lat=lat, lng=lng)
                else:
                    gym = check_gyms
                    gym.search_id = search.id

                    check_locations = Location.query.with_parent(gym).filter_by(address=address).first()
                    # if new location, create location
                    if check_locations == None:
                        location = Location(place_id=place_id, address=address,
                                            search_id=search.id, link=maps_link, lat=lat, lng=lng)
                        # if location exists update its search id, so we know it corresponds to this search.
                    else:
                        location = check_locations
                        location.search_id = search.id

                gym.locations.append(location)
                search.gyms.append(gym)

                link_and_description = scrape(query, gym_name)
                link = link_and_description[0]
                description = link_and_description[1]

                # check gym info
                if gym.info == []:
                    info = Info(link=link, description=description, search_id=search.id, gym_id=gym.id)
                # else if it has info, if info is different add a new info
                else:
                    #links = [i.link for i in gym.info]
                    check_info = Info.query.with_parent(gym).filter_by(link=link).first()
                    # if info is new, create new Info object
                    # this should prevent duplicate info objects, but idk if it works
                    if check_info == None:
                        info = Info(link=link, description=description, search_id=search.id, gym_id=gym.id)
                    # if info is right, just update search id
                    else:
                        info = check_info
                        info.search_id = search.id

                gym.info.append(info)

    else:
        search = check_searches
        center_lat = search.lat
        center_lng = search.lng
        # even though the search has been done before, we still need to update info
        for gym in search.gyms:
            # update
            gym.search_id = search.id
            #send coordinates api
            for location in gym.locations:
                if location.search_id == search.id: 
                    if locations_coordinates == {}:
                        locations_coordinates['center'] = [center_lat, center_lng]
                        locations_coordinates['gyms']=[{'name': gym.name, 'coordinates':[location.lat, location.lng], 
                        'link': location.link, 'address': location.address}]
                    else:   
                        locations_coordinates['gyms'].append({'name': gym.name, 
                            'coordinates':[location.lat, location.lng], 'link': location.link, 
                            'address': location.address})

            #if there is only one info object, that must be the info
            if len(gym.info) == 1: 
                gym.info[0].search_id = search.id
    while True:
        try:
            db.session.commit()
        except exc.OperationalError:
            print("second exception")
        break
    gyms = search.gyms

    if len(gyms) == 0:
        flash('Did not find any gyms passes! This can either be because there are none or our servers are down.' + 
            ' Please try again at a later time.', 'danger')
    elif len(gyms) == 1:
        flash('Found {} pass at this gyms by {}!'.format(len(gyms), query), 'success')
    else:
        flash('Found {} passes at these gyms by {}!'.format(len(gyms), query), 'success')
    return render_template('results.html', title="Search Results", search=search)


@main.route("/scrape", methods=['GET', 'POST'])
@login_required
def pre_scrape():
    #used for pre-scraping to set up db 
    with open('./gym/static/csv/short_cities_list.csv', 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        # Opens csv file with names of cities
        for line in csv_reader:
            place=line[1]+", "+line[2]+", USA"
            place=place.lower()
            print(place)
            check_searches = Search.query.filter_by(user_input=place).first()
            # if this is a new search
            if check_searches == None:
                #center lat,lng are the coordinates of the gym 
                center_lat, center_lng, info = maps_scrape(place)
                search = Search(user_input=place,lat=center_lat, lng=center_lng)
                db.session.add(search)
                db.session.flush()

                if info != 0:
                    # for each gym that is found
                    for result in info['results']:
                        place_id = result['place_id']
                        lat = result['geometry']['location']['lat']
                        lng = result['geometry']['location']['lng']

                        maps_link, gym_name, address = get_place_details(place_id)
                        # this photo reference can be used in the google places photo api
                        # to get a posted picture, but it is not their logo
                        # image = result['photo_reference']

                        check_gyms = Gym.query.filter_by(name=gym_name).first()
                        # if this is a new gym, create the Gym, a Location, and append
                        if check_gyms == None:
                            gym = Gym(name=gym_name, search_id=search.id)
                            print('New: ', gym)
                            location = Location(place_id=place_id, address=address, search_id=search.id,
                                                link=maps_link, lat=lat, lng=lng)
                        else:
                            gym = check_gyms
                            print('Old: ', gym)
                            gym.search_id = search.id

                            check_locations = Location.query.with_parent(gym).filter_by(address=address).first()
                            # if new location, create location
                            if check_locations == None:
                                location = Location(place_id=place_id, address=address,
                                                    search_id=search.id, link=maps_link, lat=lat, lng=lng)
                                # if location exists update its search id, so we know it corresponds to this search.
                            else:
                                location = check_locations
                                location.search_id = search.id

                        gym.locations.append(location)
                        search.gyms.append(gym)

                        link_and_description = scrape(place, gym_name)
                        link = link_and_description[0]
                        description = link_and_description[1]
                        print(link)
                        # check gym info
                        if gym.info == []:
                            info = Info(link=link, description=description, search_id=search.id, gym_id=gym.id)
                        # else if it has info, if info is different add a new info
                        else:
                            #links = [i.link for i in gym.info]
                            check_info = Info.query.with_parent(gym).filter_by(link=link).first()
                            # if info is new, create new Info object
                            if check_info == None:
                                info = Info(link=link, description=description, search_id=search.id, gym_id=gym.id)
                            # if info is right, just update search id
                            else:
                                info = check_info
                                info.search_id = search.id

                        gym.info.append(info)

            else:
                search = check_searches
                center_lat = search.lat
                center_lng = search.lng
                # even though the search has been done before, we still need to update info
                for gym in search.gyms:
                    # update
                    gym.search_id = search.id

                    #if there is only one info object, that must be the info
                    if len(gym.info) == 1: 
                        gym.info[0].search_id = search.id  

            db.session.commit()
    return render_template('about.html')

