import re
import csv
import requests
from bs4 import BeautifulSoup
from pathlib import Path
#from search.routes import Search
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
#Headers modifies how requests contacts google.com; without it Google recongizes the scraper and returns incorrect links


#will be imported from user's search in future

def query_first_page(location):
    #Because accessing the second page of results from the first is hard, we have two
    #different functions for them.
    location.replace(" ", "+")
    #Replaces any spaces the user types with plus signs so no errors are encountered.
    search_url="https://google.com/search?q=free+guest+pass+gyms+in"+location
    first_web_page=requests.get(search_url, headers=headers)
    #Retrieves the first page of results via a get request
    return first_web_page

def query_second_page(location):
    location.replace(" ", "+")
    search_url="https://google.com/search?q=free+guest+pass+gyms+in"+location+"&ei=mjBnW76PLIHX5gKWppOQBg&start=10&sa=N&biw=1396&bih=690"
    second_web_page=requests.get(search_url, headers=headers)
    #Operates in the same manner as the other query function, but has an added string on the link to move to second page

    return second_web_page

def gyms_parser(response):
    html_soup = BeautifulSoup(response.text, 'html.parser')
    search_results= html_soup.find_all('h3', class_ = 'r')
    #Turns the get request into soup and gets the results, which are a list of h3 divisons

    return search_results

def link_organizer(google_list):
    link_list=[]
    for gym_link_list in google_list:
        for gym_link in gym_link_list:
            #There are two for loops because there are two lists, one for the first page, one for the second.
            #We have to loop through the both lists and everything each contains.
            gym_link = gym_link.a['href']
            gym_link = gym_link.replace("/url?q=", "")
            #Gets the actual link and removes extra stuff on it to make the link "clickable"
            if blacklisted_links(gym_link)==None:
                if gym_name_library(gym_link):
                    link_list.append(gym_link)
                #Checks the link is actually for a gym


    return link_list

def blacklisted_links(link):
    with open('./gym/search/blacklist.csv', 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        # Opens csv file with website names that aren't gyms

        for line in csv_reader:
            if str(line[0]) in link:
                return True
                # Checks gym link and returns


def gym_name_finder(gym_links):
    gym_names=[]
    modified_links=[]
    count=0
    for gym_link in gym_links:
        actual_name=gym_name_library(gym_link)
        if actual_name:
            if actual_name not in gym_names:
                gym_names.append(actual_name)
                modified_links.append(gym_link)
        else:
            gym_names.append('Gym Name Not Found')
        #Checks gym link to see what the gym name is in how
        #one would usually write it.
        count+=1
    gym_names_and_links=(gym_names, modified_links)

    return gym_names_and_links

def gym_name_library(gym_link):

    with open('./gym/search/gym_library.csv', 'r') as csv_file:
        csv_reader=csv.reader(csv_file)
        #Opens csv file with gym link names and actual gym names

        for line in csv_reader:
            if line[0] in gym_link:
                gym_name=line[1]
                gym_name = gym_name.replace("\t", "")
                #For some reason the second column has \t in front of every gym name, so this removes that
                return gym_name
                #Checks gym link and returns

def image_finder(gym_names):
    gym_images_list=[]

    for gym_name in gym_names:
        gym_image = gym_name.replace(" ", "_")
        gym_image = gym_image + '.jpg'
        # For some reason the second column has \t in front of every gym image gile name, so this removes that
        my_file = Path("./gym/static/gym_pics"+gym_image)
        if my_file.is_file():
            # file exists
            gym_images_list.append(gym_image)
        else:
            gym_images_list.append('default.jpg')
        # Returns image file name

    return gym_images_list

# def location_finder(location, gym_names):
#     locations=[]
#     location.replace(" ", "+")
#     for gym_name in gym_names:
#         gym_name.replace(" ", "+")
#
#         locations_search_url = "https://www.google.com/search?q="+gym_name+"in"+location
#         locations_web_page = requests.get(locations_search_url, headers=headers)
#
#         html_soup = BeautifulSoup(locations_web_page.text, 'html.parser')
#         # locations_results = html_soup.find_all('div', {"class": "section-result-details-container"}).find('span', {"class": "section-result-location"})
#         # for location in locations_results:
#         #     locations.append(location.text)
#     # print(locations)
#     # print(locations_results)

def description(gym_names):
    gym_descriptions = []
    with open('./gym/search/descriptions.csv', 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        # Opens csv file with website names that aren't gyms

        for line in csv_reader:
            for gym_name in gym_names:
                if str(line[0]) in gym_name:
                    gym_description=line[1]
                    gym_description = gym_description.replace("\t", "")
                    gym_descriptions.append(gym_description)

    return gym_descriptions





def scrape(location):

    list_of_results=[]

    google_search_first=query_first_page(location)
    list_of_results_first=gyms_parser(google_search_first)
    list_of_results.append(list_of_results_first)

    google_search_second = query_first_page(location)
    list_of_results_second=gyms_parser(google_search_second)
    list_of_results.append(list_of_results_second)

    list_of_links=link_organizer(list_of_results)
    list_of_gym_names_and_links=gym_name_finder(list_of_links)
    list_of_gym_names=list_of_gym_names_and_links[0]
    list_of_links = list_of_gym_names_and_links[1]
    list_of_gym_images=image_finder(list_of_gym_names)
    list_of_gym_descriptions=description(list_of_gym_names)
    
    print(list_of_gym_descriptions)


    results = []

    for i in range(len(list_of_links)):
        results.append([list_of_links[i], list_of_gym_names[i],list_of_gym_images[i], list_of_gym_descriptions[i]])


    return results



if __name__ == '__main__':
    scrape()