import re
import csv
import requests
from bs4 import BeautifulSoup
from pathlib import Path

# from search.routes import Search
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}


# Headers modifies how requests contacts google.com; without it Google recongizes the scraper and returns incorrect links


# will be imported from user's search in future

def query_google_search(location, gym_name):
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
            print(gym_link)
            if blacklist(gym_link)==None:
                return gym_link
    else:
        return gym_link




def gym_link_library(gym_name):
    with open('./gym/search/gym_links.csv', 'r') as csv_file:
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
    with open('./gym/search/descriptions.csv', 'r') as csv_file:
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
    with open('./gym/search/blacklist.csv', 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        for line in csv_reader:
            if str(line[0]) in link:
                return True

def scrape(location, gym_name):
    gym_link = str(query_google_search(location, gym_name))
    gym_description = str(description(gym_name))
    results = [gym_link,gym_description]

    return results


if __name__ == '__main__':
    results = scrape('nyc','Crunch')
    print(results)