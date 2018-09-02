import requests 

#top secret api key
API_KEY = 'AIzaSyBxq6oC2dG2L7oHlKG2jaBeYUMjye8fzDQ'

#get coordinates of the location inputted so that we can accurately search for 
#gyms in a 10,000m radius around there 
def find_place(location):
	request_base = 'https://maps.googleapis.com/maps/api/place/findplacefromtext/json?'
	inputtype='textquery'
	fields='geometry,name'
	r = requests.get(request_base + 'input={}&inputtype={}&fields={}&key={}'.format(location,inputtype,fields,API_KEY)).json()
	if r['status'] != 'ZERO_RESULTS':
		lat = r['candidates'][0]['geometry']['location']['lat']
		lng = r['candidates'][0]['geometry']['location']['lng']
		name = r['candidates'][0]['name']
		return lat,lng, name
	else:
		return 0,0,0

#gets the json file containing address, location, name, opening_now, place_id, etc.
def text_search(lat,lng, name):
	radius=10000
	typ='gym'
	request_base='https://maps.googleapis.com/maps/api/place/textsearch/json?query=free%20guest%20pass%20gyms%20%20'
	request = request_base + '&type={}&location={},{}&radius={}&key={}'.format(typ,lat, lng,radius,API_KEY)
	r = requests.get(request).json()
	return r

#calls on find places api to get coordinates and name and then calls on 
#text search api to get info 
def maps_scrape(location):
	location.replace(" ", "%20")
	lat,lng, name = find_place(location)
	if (lat, lng, name) != (0,0,0):
		results = text_search(lat,lng,name)
		return lat, lng, results
	else:
		return 'ZERO_RESULTS'

#uses details api to get a place's details given a place id
def get_place_details(place_id):
	request_base = 'https://maps.googleapis.com/maps/api/place/details/json?'
	fields = 'url,name'
	r = requests.get(request_base + 'placeid={}&fields={}&key={}'.format(place_id, fields, API_KEY)).json()
	return r 

if __name__ == '__main__':
	maps_scrape('new york city')