from _sqlite3 import OperationalError
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
import time
from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from gym import db, mongo
from gym.models import Search, Gym, Location, Post, Info
from gym.search.forms import SearchForm
from gym.search.scraper import scrape
from gym.search.maps_scraper import maps_scrape, get_place_details, abbreviation_fixer
from flask_login import login_required
from flask_pymongo import PyMongo
import json
import csv
from boto.s3.connection import S3Connection
import os

try: 
    API_KEY= S3Connection(os.environ['API_KEY'])
except: 
    API_KEY= os.environ['API_KEY']
assert API_KEY


API_KEY = os.environ['API_KEY']
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
    return render_template('home.html', form=form, posts=posts, key=API_KEY)

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
    locations_coordinates.clear()
    query=abbreviation_fixer(query)

    #initialize DB
    search=mongo.db.search
    gym = mongo.db.gym
    location = mongo.db.location
    info = mongo.db.info           

    check_searches = search.find_one({'user_input':query})

    # if this is a new search
    if check_searches == None:
            #center lat,lng are the coordinates of the gym

        center_lat, center_lng, data = maps_scrape(query)
        current_search = {'gym_id':[],'user_input':query,'lat':center_lat, 'lng':center_lng}
        search.insert_one(current_search)
        #print(current_search['_id'])

        if data != 0:
            # for each gym that is found
            for result in data['results']:
                place_id = result['place_id']
                lat = result['geometry']['location']['lat']
                lng = result['geometry']['location']['lng']

                maps_link, gym_name, address = get_place_details(place_id)
                print(gym_name)
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

                check_gyms = gym.find_one({'name':gym_name})
                # if this is a new gym, create the Gym, a Location, and append
                if check_gyms == None:
                    current_gym = {'search_id':[current_search['_id']], 'location_id':[], 'info_id': [],'name':gym_name}
                    gym.insert_one(current_gym)

                    current_location = {'search_id':[current_search['_id']],'gym_id':current_gym['_id'],'place_id':place_id, 'name':gym_name,
                        'address':address,'link':maps_link, 'lat':lat, 'lng':lng}
                    location.insert_one(current_location)
                    current_gym['location_id'].append(current_location['_id'])
                else:
                    current_gym = check_gyms

                    if current_gym['search_id'][0] != current_search['_id']:
                        current_gym['search_id'].append(current_search['_id'])

                    check_locations = location.find_one({'address':address})
                    # if new location, create location
                    if check_locations == None:
                        current_location = {'search_id':[current_search['_id']],'gym_id':current_gym['_id'],'place_id':place_id, 'name':gym_name,   
                            'address':address,'link':maps_link, 'lat':lat, 'lng':lng}
                        location.insert_one(current_location)
                        current_gym['location_id'].append(current_location['_id'])
                        # if location exists update its search id, so we know it corresponds to this search.
                    else:
                        current_location = check_locations
                        current_location['search_id'].append(current_search['_id'])

                #add gym to search if its not there already 
                if current_gym['_id'] not in current_search['gym_id']:
                    current_search['gym_id'].append(current_gym['_id'])

                link_and_description = scrape(query, gym_name)
                link = link_and_description[0]
                description = link_and_description[1]

                
                # check gym info
                if current_gym['info_id'] == []:
                    current_info = {'search_id':[current_search['_id']], 'gym_id':current_gym['_id'], 'link':link, 'description':description, 'name':gym_name}
                    info.insert_one(current_info)
                    current_gym['info_id'].append(current_info['_id'])
                # else if it has info, if info is different add a new info
                else:
                    #links = [i.link for i in gym.info]
                    check_info = info.find_one({'link':link})
                    # if info is new, create new Info object
                    if check_info == None:
                        current_info = {'search_id':[current_search['_id']], 'gym_id':current_gym['_id'],'link':link, 'description':description, 'name':gym_name}
                        info.insert_one(current_info)
                        current_gym['info_id'].append(current_info['_id'])
                    # if info is right, just update search id
                    else:
                        current_info = check_info
                        if current_search['_id'] not in current_info['search_id']:
                            current_info['search_id'].append(current_search['_id'])

                info.save(current_info)
                gym.save(current_gym)
                location.save(current_location)

    else:
        current_search = check_searches
        center_lat = current_search['lat']
        center_lng = current_search['lng']
        # even though the search has been done before, we still need to update info
        for gym_id in current_search['gym_id']:
            # update
            current_gym = gym.find_one({'_id':gym_id})
            #send coordinates api
            for location_id in current_gym['location_id']:
                current_location = location.find_one({'_id':location_id})
                if current_search['_id'] in current_location['search_id']: 
                    if locations_coordinates == {}:
                        locations_coordinates['center'] = [center_lat, center_lng]
                        locations_coordinates['gyms']=[{'name': current_gym['name'], 'coordinates':[current_location['lat'], current_location['lng']], 
                        'link': current_location['link'], 'address': current_location['address']}]
                    else:   
                        locations_coordinates['gyms'].append({'name': current_gym['name'], 
                            'coordinates':[current_location['lat'], current_location['lng']], 'link': current_location['link'], 
                            'address': current_location['address']})

    search.save(current_search)
    gyms = current_search['gym_id']

    if len(gyms) == 0:
        flash('Did not find any gyms passes! This can either be because there are none or our servers are down.' + 
            ' Please try again at a later time.', 'danger')
    elif len(gyms) == 1:
        flash('Found {} pass at this gym by {}!'.format(len(gyms), query), 'success')
    else:
        flash('Found {} passes at these gyms by {}!'.format(len(gyms), query), 'success')
    return render_template('results.html', title="Search Results", current_search=current_search, search=search, 
        gym=gym, info=info, location=location, key=API_KEY)


@main.route("/scrape", methods=['GET', 'POST'])
@login_required
def pre_scrape():
    #used for pre-scraping to set up db 
    with open('./gym/static/csv/short_cities_list.csv', 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        # Opens csv file with names of cities
        for line in csv_reader:
            query=line[1]+", "+line[2]+", USA"
            query=query.lower()
            print(query)

            #initialize DB
            search=mongo.db.search
            gym = mongo.db.gym
            location = mongo.db.location
            info = mongo.db.info           

            check_searches = search.find_one({'user_input':query})

            # if this is a new search
            if check_searches == None:
                    #center lat,lng are the coordinates of the gym

                center_lat, center_lng, data = maps_scrape(query)
                current_search = {'gym_id':[],'user_input':query,'lat':center_lat, 'lng':center_lng}
                search.insert_one(current_search)

                if data != 0:
                    # for each gym that is found
                    for result in data['results']:
                        place_id = result['place_id']
                        lat = result['geometry']['location']['lat']
                        lng = result['geometry']['location']['lng']

                        maps_link, gym_name, address = get_place_details(place_id)
                        print(gym_name)
                        # this photo reference can be used in the google places photo api
                        # to get a posted picture, but it is not their logo
                        # image = result['photo_reference']

                        check_gyms = gym.find_one({'name':gym_name})
                        # if this is a new gym, create the Gym, a Location, and append
                        if check_gyms == None:
                            current_gym = {'search_id':[current_search['_id']], 'location_id':[], 'info_id': [],'name':gym_name}
                            gym.insert_one(current_gym)

                            current_location = {'search_id':[current_search['_id']],'gym_id':current_gym['_id'],'place_id':place_id, 'name':gym_name,
                                'address':address,'link':maps_link, 'lat':lat, 'lng':lng}
                            location.insert_one(current_location)
                            current_gym['location_id'].append(current_location['_id'])
                        else:
                            current_gym = check_gyms

                            if current_gym['search_id'][0] != current_search['_id']:
                                current_gym['search_id'].append(current_search['_id'])

                            check_locations = location.find_one({'address':address})
                            # if new location, create location
                            if check_locations == None:
                                current_location = {'search_id':[current_search['_id']],'gym_id':current_gym['_id'],'place_id':place_id, 'name':gym_name,   
                                    'address':address,'link':maps_link, 'lat':lat, 'lng':lng}
                                location.insert_one(current_location)
                                current_gym['location_id'].append(current_location['_id'])
                                # if location exists update its search id, so we know it corresponds to this search.
                            else:
                                current_location = check_locations
                                current_location['search_id'].append(current_search['_id'])

                        #add gym to search if its not there already 
                        if current_gym['_id'] not in current_search['gym_id']:
                            current_search['gym_id'].append(current_gym['_id'])

                        link_and_description = scrape(query, gym_name)
                        link = link_and_description[0]
                        description = link_and_description[1]

                        
                        # check gym info
                        if current_gym['info_id'] == []:
                            current_info = {'search_id':[current_search['_id']], 'gym_id':current_gym['_id'], 'link':link, 'description':description, 'name':gym_name}
                            info.insert_one(current_info)
                            current_gym['info_id'].append(current_info['_id'])
                        # else if it has info, if info is different add a new info
                        else:
                            #links = [i.link for i in gym.info]
                            check_info = info.find_one({'link':link})
                            # if info is new, create new Info object
                            if check_info == None:
                                current_info = {'search_id':[current_search['_id']], 'gym_id':current_gym['_id'],'link':link, 'description':description, 'name':gym_name}
                                info.insert_one(current_info)
                                current_gym['info_id'].append(current_info['_id'])
                            # if info is right, just update search id
                            else:
                                current_info = check_info
                                if current_search['_id'] not in current_info['search_id']:
                                    current_info['search_id'].append(current_search['_id'])

                        info.save(current_info)
                        gym.save(current_gym)
                        location.save(current_location)

            else:
                current_search = check_searches

            search.save(current_search)           
    return render_template('about.html')

