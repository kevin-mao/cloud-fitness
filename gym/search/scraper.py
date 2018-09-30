import re
import csv
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import json
import os 

API_KEY = os.environ['API_KEY']
BING_KEY = os.environ['BING_KEY']


# from search.routes import Search
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}


# Headers modifies how requests contacts google.com; without it Google recongizes the scraper and returns incorrect links


# will be imported from user's search in future
def query_bing_search(location, gym_name):
    gym_link=gym_link_library(gym_name)

    if gym_link==None:
        search_url = "https://api.cognitive.microsoft.com/bing/v7.0/search"
        search_term = "free "+gym_name+" guest passes in "+location
        headers = {"Ocp-Apim-Subscription-Key":BING_KEY}
        params = {"q": search_term, "textDecorations": True, "textFormat": "HTML"}
        response = requests.get(search_url, headers=headers, params=params)
        response.raise_for_status()
        search_results = response.json()
        json.dumps(search_results)
        #print(search_results)

        for result in search_results['webPages']['value']:
            link=result['url']
            print(gym_name+": "+link)
            if blacklist(link)==False:
                return link
    else:
        return gym_link

def query_google_search(location,gym_name):
    gym_link=gym_link_library(gym_name)

    if gym_link==None:
            # Because accessing the second page of results from the first is hard, we have two
        # different functions for them.
        location.replace(" ", "+")
        # Replaces any spaces the user types with plus signs so no errors are encountered.
        
        search_url = "https://google.com/search?q=free" + gym_name + "guest+pass+in" + location
        web_page = requests.get(search_url, headers=headers)
        # Searches for gym and area
        
        html_soup = BeautifulSoup(web_page.text, 'html.parser')
        gym_links = html_soup.find_all('div', {'class': 'rc'})
        
        # Turns the get request into soup and gets the first result
        for gym_link in gym_links:
            gym_link = gym_link.a['href']
            gym_link = gym_link.replace("/url?q=", "")
            if "24hrs" in gym_link:
                return "https://www.24hourfitness.com/membership/free-pass/#step/1"
            if blacklist(gym_link)==False:
                return gym_link
    else:
        return gym_link


def gym_link_library(gym_name):
    with open('./gym/static/csv/gym_links.csv', 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        # Opens csv file with website names that aren't gyms
        gym_link=None
        for line in csv_reader:

            if str(line[0]) in gym_name:
                gym_link = line[1]
                gym_link = gym_link.replace("\t", "")
    
    return gym_link


def description(gym_name):
    gym_descriptions = []
    with open('./gym/static/csv/descriptions.csv', 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        # Opens csv file with website names that aren't gyms
        
        for line in csv_reader:

            if str(line[0]) in gym_name:

                gym_description = line[1]
                gym_description = gym_description.replace("\t", "")
                return gym_description

            else:
                gym_description='Cool gym pass!'

    return gym_description

def blacklist(link):
    with open('./gym/static/csv/blacklist.csv', 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        for line in csv_reader:
            if str(line[0]) in link:
                return True
        return False

def scrape(location, gym_name):
    gym_link = str(query_bing_search(location, gym_name))
    gym_description = str(description(gym_name))
    results = [gym_link,gym_description]

    return results

if __name__ == '__main__':
    results = scrape('nyc','Crunch')
    print(results)