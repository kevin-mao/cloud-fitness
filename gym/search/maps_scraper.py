import requests 

#top secret api key
API_KEY = 'AIzaSyBxq6oC2dG2L7oHlKG2jaBeYUMjye8fzDQ'

#get coordinates of the location inputted so that we can accurately search for 
#gyms in a 10,000m radius around there 
def get_coordinates(location):
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
def scrape(lat,lng, name):
	radius=10000
	typ='gym'
	request_base='https://maps.googleapis.com/maps/api/place/textsearch/json?query=free%20guest%20pass%20gyms%20in%20'
	request = request_base + '{}&type={}&location={},{}&radius={}&key={}'.format(name,typ,lat, lng,radius,API_KEY)
	r = requests.get(request).json()
	return r

def maps_scrape(location):
	location.replace(" ", "%20")
	lat,lng, name = get_coordinates(location)
	if (lat, lng, name) != (0,0,0):
		results = scrape(lat,lng,name)
		return results
	else:
		return 'ZERO_RESULTS'
def get_place_details(place_id):
	request_base = 'https://maps.googleapis.com/maps/api/place/details/json?'
	fields = 'url,name'
	r = requests.get(request_base + 'placeid={}&fields={}&key={}'.format(place_id, fields, API_KEY)).json()
	return r 

if __name__ == '__main__':
	process('new york city')