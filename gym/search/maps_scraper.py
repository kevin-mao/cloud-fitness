import requests 
import csv 
import os 
from boto.s3.connection import S3Connection
import os
import urllib.request

try: 
    API_KEY, BING_KEY= S3Connection(os.environ['API_KEY'], os.environ['BING_KEY'])
except: 
    API_KEY= os.environ['API_KEY']
    BING_KEY = os.environ['BING_KEY']

assert API_KEY, BING_KEY


#get coordinates of the location inputted so that we can accurately search for 
def find_place(location):
    request_base = 'https://maps.googleapis.com/maps/api/place/findplacefromtext/json?'
    inputtype='textquery'
    fields='geometry,name'
    r = requests.get(request_base + 'input={}&inputtype={}&fields={}&key={}'.format(location,inputtype,fields,API_KEY)).json()
    if r['status'] != 'ZERO_RESULTS' and r['status'] != 'OVER_QUERY_LIMIT':
        lat = r['candidates'][0]['geometry']['location']['lat']
        lng = r['candidates'][0]['geometry']['location']['lng']
        name = r['candidates'][0]['name']
        return lat,lng, name
    else:
        return 0,0,0

#gets the json file containing address, location, name, opening_now, place_id, etc.
def text_search(lat,lng, name):
    radius=6000
    typ='gym'
    request_base='https://maps.googleapis.com/maps/api/place/textsearch/json?query=free%20guest%20pass%20gyms%20'
    request = request_base + '&type={}&location={},{}&radius={}&key={}'.format(typ,lat, lng,radius,API_KEY)
    r = requests.get(request).json()
    return r

# those weird where the franchise has a different name for each location
def check_name(name):
    parts = name.split(" ")
    bad_names = ['Crunch', 'Equinox', 'Intoxx', 'GoodLife', 'Planet', 'Anytime', 'Blink', 'BodyScapes', 'EōS']
    for bn in bad_names: 
        if bn in parts:
            name = parts[0] + ' Fitness'
    if '24' in parts: 
        name = parts[0] + ' Hour Fitness'
    if 'YMCA' in parts:
        name = "YMCA"
    if 'Powerhouse' in name: 
        name = 'Powerhouse Gym'
    if name == 'LA FITNESS':
        name = 'LA Fitness'
    if 'Jewish Community Center' in name or 'JCC' in name:
        name = 'Jewish Community Center'
    return name

#uses details api to get a place's details given a place id
def get_place_details(place_id):
    request_base = 'https://maps.googleapis.com/maps/api/place/details/json?'
    fields = 'formatted_address,url,name'
    r = requests.get(request_base + 'placeid={}&fields={}&key={}'.format(place_id, fields, API_KEY)).json()
    url = r['result']['url']
    gym_name = check_name(r['result']['name'])
    address = r['result']['formatted_address']
    return url, gym_name, address

#calls on find places api to get coordinates and name and then calls on 
#text search api to get info 
def maps_scrape(location):
    location.replace(" ", "%20")
    #get the location of the search 
    lat,lng, name = find_place(location)
    if (lat, lng, name) != (0,0,0):
        #get gym by the area 
        results = text_search(lat,lng,name)
        return lat, lng, results
    else:
        return 0,0,0


#the way we scraped cities, we used full state name not abbreviated states 
#used to fix autocomplete cities 
def abbreviation_fixer(query):
    with open('./gym/static/csv/state_names.csv', 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        # Opens csv file with list of state names and abbreviations
        for line in csv_reader:
            abbreviation = " "+ line[1].lower() + ","
            if abbreviation in query:
                state_name=" "+line[0]+","
                # if the state abbreviation is in the search, replace with with the full name
                query = query.replace(abbreviation, state_name).lower()
    if 'nyc' in query.lower():
        query = 'new york, new york, usa'
    print(query)
    return query


if __name__ == '__main__':
    maps_scrape('new york city')